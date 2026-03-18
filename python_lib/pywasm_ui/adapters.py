from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence, cast
from urllib.parse import parse_qs

from .communication import (
    FastAPIWasmAsyncReceiver,
    FastAPIWasmCommandSender,
    WasmAppCommunication,
)
from .frontend_assets import get_packaged_frontend_root
from .logging_utils import get_logger
from .session import ProtocolViolationError, PyWasmSession, create_session_factory
from .widgets import WasmWidget

logger = get_logger(__name__)

# Optional framework symbols are initialized here so static analyzers do not
# report them as undefined when imports are unavailable or TYPE_CHECKING is true.
FileResponse = None
JSONResponse = None
jsonify = None
send_from_directory = None
StaticFiles = None

if TYPE_CHECKING:
    from fastapi import WebSocket
    from fastapi.staticfiles import StaticFiles
    from pywasm_ui.style_template import StyleTemplate
    from fastapi.responses import FileResponse, JSONResponse
    from flask import jsonify, send_from_directory
    from starlette.websockets import WebSocketDisconnect
else:
    try:
        from fastapi import WebSocket
        from fastapi.responses import FileResponse, JSONResponse
        from fastapi.staticfiles import StaticFiles
        from starlette.websockets import WebSocketDisconnect
    except ImportError:  # pragma: no cover - optional dependency fallback
        WebSocket = Any  # type: ignore[misc,assignment]
        FileResponse = None
        JSONResponse = None
        StaticFiles = None

        class WebSocketDisconnect(Exception):
            """Fallback exception type when Starlette/FastAPI is unavailable."""

    try:
        from flask import jsonify, send_from_directory
    except ImportError:  # pragma: no cover - optional dependency fallback
        jsonify = None
        send_from_directory = None


def _extract_flask_requested_token(ws: object) -> str | None:
    environ = getattr(ws, "environ", None)
    if not isinstance(environ, dict):
        return None

    query_string = environ.get("QUERY_STRING")
    if not isinstance(query_string, str) or not query_string:
        return None

    values = parse_qs(query_string).get("session_token")
    if not values:
        return None

    token = values[0]
    return token if token else None


def _simulated_latency_seconds() -> float:
    raw = os.getenv("PYWASM_SIMULATED_LATENCY_MS", "0")
    try:
        ms = float(raw)
    except ValueError:
        return 0.0
    if ms <= 0:
        return 0.0
    return ms / 1000.0


def _session_ttl_seconds() -> float:
    raw = os.getenv("PYWASM_SESSION_TTL_SECONDS", "1800")
    try:
        ttl = float(raw)
    except ValueError:
        return 1800.0
    return 1800.0 if ttl <= 0 else ttl


def _max_active_sessions() -> int:
    raw = os.getenv("PYWASM_MAX_ACTIVE_SESSIONS", "1024")
    try:
        value = int(raw)
    except ValueError:
        return 1024
    return 1024 if value <= 0 else value


def _allowed_ws_origins() -> set[str] | None:
    raw = os.getenv("PYWASM_ALLOWED_WS_ORIGINS", "").strip()
    if not raw:
        return None
    values = {origin.strip() for origin in raw.split(",") if origin.strip()}
    return values or None


def _is_origin_allowed(origin: str | None, allowed_origins: set[str] | None) -> bool:
    if allowed_origins is None:
        return True
    if "*" in allowed_origins:
        return True
    if origin is None:
        return False
    return origin in allowed_origins


def _prune_active_sessions(
    active_sessions: dict[str, tuple[PyWasmSession, float]],
    *,
    now: float,
    ttl_seconds: float,
    max_sessions: int,
) -> None:
    expired_tokens = [
        token
        for token, (_session, last_seen) in active_sessions.items()
        if now - last_seen > ttl_seconds
    ]
    for token in expired_tokens:
        active_sessions.pop(token, None)
    if expired_tokens:
        logger.debug("Pruned %d expired sessions", len(expired_tokens))

    if len(active_sessions) <= max_sessions:
        return

    overflow = len(active_sessions) - max_sessions
    oldest = sorted(active_sessions.items(), key=lambda item: item[1][1])
    for token, _entry in oldest[:overflow]:
        active_sessions.pop(token, None)
    logger.warning("Pruned %d sessions due to max session limit (%d)", overflow, max_sessions)


def _token_preview(token: str | None) -> str:
    if not token:
        return "<none>"
    if len(token) <= 8:
        return token
    return f"{token[:4]}...{token[-4:]}"


def _default_security_headers() -> dict[str, str]:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'; connect-src 'self' ws: wss:; img-src 'self' data:; media-src 'self' https: data: blob:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; font-src 'self' https://fonts.gstatic.com; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval'; base-uri 'self'; frame-ancestors 'none'",
    }


def _apply_security_headers(response: object) -> object:
    headers = getattr(response, "headers", None)
    if headers is None:
        return response
    for key, value in _default_security_headers().items():
        if key not in headers:
            headers[key] = value
    return response


def _normalize_page_route(route: str) -> str:
    value = route.strip()
    if not value:
        return "/"
    if not value.startswith("/"):
        value = f"/{value}"
    if value != "/" and value.endswith("/"):
        value = value.rstrip("/")
    return value


def _resolve_static_file(client_root: Path, relative_path: str) -> Path | None:
    target = (client_root / relative_path).resolve()
    if not (client_root.exists() and target.exists() and target.is_file()):
        return None
    if client_root not in target.parents:
        return None
    return target


def _prepare_frontend_mount(
    client_root: str | Path,
    pages: dict[str, str] | None,
    reserved_paths: Sequence[str],
) -> tuple[Path, dict[str, str], set[str]]:
    root = Path(client_root).resolve()
    route_to_file = {
        _normalize_page_route(route): file_path
        for route, file_path in (pages or {}).items()
    }
    excluded = {value.strip("/") for value in reserved_paths if value.strip("/")}
    return root, route_to_file, excluded


def _normalize_route_prefix(route_prefix: str) -> str:
    value = route_prefix.strip()
    if not value:
        raise ValueError("route_prefix must not be empty")
    if not value.startswith("/"):
        value = f"/{value}"
    if len(value) > 1 and value.endswith("/"):
        value = value.rstrip("/")
    return value


def _first_path_segment(path_value: str) -> str | None:
    value = path_value.strip()
    if not value:
        return None
    if value.startswith("/"):
        value = value[1:]
    if not value:
        return None
    return value.split("/", 1)[0]


def _merge_reserved_paths(
    reserved_paths: Sequence[str],
    *,
    ws_path: str,
    health_path: str | None,
    assets_route_prefix: str,
) -> tuple[str, ...]:
    merged: list[str] = []
    for value in reserved_paths:
        cleaned = value.strip("/")
        if cleaned and cleaned not in merged:
            merged.append(cleaned)

    for source in (ws_path, health_path, assets_route_prefix):
        if source is None:
            continue
        segment = _first_path_segment(source)
        if segment and segment not in merged:
            merged.append(segment)

    return tuple(merged)


def mount_fastapi_frontend(
    app: object,
    client_root: str | Path,
    *,
    index_file: str = "index.html",
    pages: dict[str, str] | None = None,
    reserved_paths: Sequence[str] = ("ws", "health"),
    spa_fallback: bool = True,
) -> None:
    """Mount static frontend routes on a FastAPI app.

    - `/` serves `index_file`
    - extra `pages` map route -> file under `client_root`
    - `/{full_path:path}` serves static assets, then optional SPA fallback
    """

    if FileResponse is None or JSONResponse is None:
        raise RuntimeError("FastAPI responses are unavailable")

    file_response = cast(Callable[..., object], FileResponse)
    json_response = cast(Callable[..., object], JSONResponse)

    root, route_to_file, excluded = _prepare_frontend_mount(
        client_root,
        pages,
        reserved_paths,
    )

    @app.get("/")  # type: ignore[attr-defined]
    async def _frontend_index() -> object:
        index = _resolve_static_file(root, index_file)
        if index is not None:
            return _apply_security_headers(file_response(index))
        return _apply_security_headers(json_response(
            status_code=503,
            content={
                "error": "frontend-not-found",
                "hint": f"Missing {root.name}/{index_file}",
            },
        ))

    for route, file_path in route_to_file.items():
        if route == "/":
            continue

        async def _page_endpoint(page_file: str = file_path) -> object:
            page = _resolve_static_file(root, page_file)
            if page is None:
                return _apply_security_headers(json_response(
                    status_code=404,
                    content={"error": "page-not-found", "path": page_file},
                ))
            return _apply_security_headers(file_response(page))

        app.get(route)(_page_endpoint)  # type: ignore[attr-defined]

    @app.get("/{full_path:path}")  # type: ignore[attr-defined]
    async def _frontend_assets(full_path: str) -> object:
        first_segment = full_path.split("/", 1)[0]
        if first_segment in excluded:
            return _apply_security_headers(json_response(status_code=404, content={"error": "not-found"}))

        target = _resolve_static_file(root, full_path)
        if target is not None:
            return _apply_security_headers(file_response(target))

        if spa_fallback:
            index = _resolve_static_file(root, index_file)
            if index is not None:
                return _apply_security_headers(file_response(index))
            return _apply_security_headers(json_response(
                status_code=503,
                content={
                    "error": "frontend-not-found",
                    "hint": f"Missing {root.name}/{index_file}",
                },
            ))

        return _apply_security_headers(json_response(status_code=404, content={"error": "not-found"}))


def register_flask_frontend(
    app: object,
    client_root: str | Path,
    *,
    index_file: str = "index.html",
    pages: dict[str, str] | None = None,
    reserved_paths: Sequence[str] = ("ws", "health"),
    spa_fallback: bool = True,
) -> None:
    """Mount static frontend routes on a Flask app.

    Mirrors `mount_fastapi_frontend` behavior for Flask projects.
    """

    if jsonify is None or send_from_directory is None:
        raise RuntimeError("Flask response helpers are unavailable")

    jsonify_fn = cast(Callable[..., object], jsonify)
    send_from_directory_fn = cast(Callable[..., object], send_from_directory)

    root, route_to_file, excluded = _prepare_frontend_mount(
        client_root,
        pages,
        reserved_paths,
    )

    @app.get("/")  # type: ignore[attr-defined]
    def _frontend_index() -> object:
        index = _resolve_static_file(root, index_file)
        if index is not None:
            return _apply_security_headers(send_from_directory_fn(str(root), index_file))
        response = jsonify_fn(
            {
                "error": "frontend-not-found",
                "hint": f"Missing {root.name}/{index_file}",
            }
        )
        cast(Any, response).status_code = 503
        return _apply_security_headers(response)

    for route, file_path in route_to_file.items():
        if route == "/":
            continue

        endpoint_suffix = route.strip("/").replace("/", "_") or "root"
        endpoint_name = f"_frontend_page_{endpoint_suffix}"

        def _page_endpoint(page_file: str = file_path) -> object:
            page = _resolve_static_file(root, page_file)
            if page is None:
                response = jsonify_fn({"error": "page-not-found", "path": page_file})
                cast(Any, response).status_code = 404
                return _apply_security_headers(response)
            return _apply_security_headers(send_from_directory_fn(str(root), page_file))

        app.add_url_rule(  # type: ignore[attr-defined]
            route,
            endpoint_name,
            _page_endpoint,
            methods=["GET"],
        )

    @app.get("/<path:full_path>")  # type: ignore[attr-defined]
    def _frontend_assets(full_path: str) -> object:
        first_segment = full_path.split("/", 1)[0]
        if first_segment in excluded:
            response = jsonify_fn({"error": "not-found"})
            cast(Any, response).status_code = 404
            return _apply_security_headers(response)

        target = _resolve_static_file(root, full_path)
        if target is not None:
            return _apply_security_headers(send_from_directory_fn(str(root), full_path))

        if spa_fallback:
            index = _resolve_static_file(root, index_file)
            if index is not None:
                return _apply_security_headers(send_from_directory_fn(str(root), index_file))
            response = jsonify_fn(
                {
                    "error": "frontend-not-found",
                    "hint": f"Missing {root.name}/{index_file}",
                }
            )
            cast(Any, response).status_code = 503
            return _apply_security_headers(response)

        response = jsonify_fn({"error": "not-found"})
        cast(Any, response).status_code = 404
        return _apply_security_headers(response)


def mount_fastapi_packaged_assets(app: object, *, route_prefix: str = "/pywasm-assets") -> Path:
    """Mount packaged PyWASMui frontend assets on a FastAPI app."""

    if StaticFiles is None:
        raise RuntimeError("FastAPI StaticFiles is unavailable")

    normalized = _normalize_route_prefix(route_prefix)
    root = get_packaged_frontend_root()
    static_files = cast(Callable[..., object], StaticFiles)
    app.mount(  # type: ignore[attr-defined]
        normalized,
        static_files(directory=str(root)),
        name="pywasm-assets",
    )
    return root


def bootstrap_fastapi_app(
    app: object,
    client_root: str | Path,
    *,
    ws_path: str = "/ws",
    server_secret: str = "dev-server-secret-change-me",
    session_factory: Callable[[], PyWasmSession] | None = None,
    initial_widgets: Sequence[WasmWidget] | None = None,
    configure_session: Callable[[PyWasmSession], None] | None = None,
    style_template: dict[str, Any] | "StyleTemplate" | None = None,
    assets_route_prefix: str = "/pywasm-assets",
    index_file: str = "index.html",
    pages: dict[str, str] | None = None,
    reserved_paths: Sequence[str] = (),
    spa_fallback: bool = True,
    health_path: str | None = "/health",
    health_payload: Mapping[str, Any] | None = None,
) -> None:
    """Wire a FastAPI app with a PyWASMui websocket and frontend routes.

    This helper is intended for quick integration and small multipage apps.
    """

    mount_fastapi_websocket(
        app,
        path=ws_path,
        server_secret=server_secret,
        session_factory=session_factory,
        initial_widgets=initial_widgets,
        configure_session=configure_session,
        style_template=style_template,
    )

    mount_fastapi_packaged_assets(app, route_prefix=assets_route_prefix)

    normalized_health_path: str | None = None
    if health_path:
        normalized_health_path = _normalize_page_route(health_path)
        payload = dict(health_payload or {"status": "ok"})

        @app.get(normalized_health_path)  # type: ignore[attr-defined]
        async def _pywasm_health() -> dict[str, Any]:
            return payload

    frontend_reserved_paths = _merge_reserved_paths(
        reserved_paths,
        ws_path=ws_path,
        health_path=normalized_health_path,
        assets_route_prefix=assets_route_prefix,
    )
    mount_fastapi_frontend(
        app,
        client_root,
        index_file=index_file,
        pages=pages,
        reserved_paths=frontend_reserved_paths,
        spa_fallback=spa_fallback,
    )


def register_flask_packaged_assets(app: object, *, route_prefix: str = "/pywasm-assets") -> Path:
    """Expose packaged PyWASMui frontend assets under a Flask route prefix."""

    if send_from_directory is None:
        raise RuntimeError("Flask response helpers are unavailable")

    normalized = _normalize_route_prefix(route_prefix)
    root = get_packaged_frontend_root()
    send_from_directory_fn = cast(Callable[..., object], send_from_directory)
    endpoint_suffix = normalized.strip("/").replace("/", "_")

    @app.get(f"{normalized}/<path:asset_path>")  # type: ignore[attr-defined]
    def _packaged_asset(asset_path: str) -> object:
        target = _resolve_static_file(root, asset_path)
        if target is None:
            return {"error": "not-found"}, 404
        return send_from_directory_fn(str(root), asset_path)

    @app.get(normalized)  # type: ignore[attr-defined]
    def _packaged_asset_root() -> object:
        return {"error": "not-found", "hint": f"Use {normalized}/<file>"}, 404

    _packaged_asset.__name__ = f"_packaged_asset_{endpoint_suffix}"
    _packaged_asset_root.__name__ = f"_packaged_asset_root_{endpoint_suffix}"
    return root


def bootstrap_flask_app(
    app: object,
    sock: object,
    client_root: str | Path,
    *,
    ws_path: str = "/ws",
    server_secret: str = "dev-server-secret-change-me",
    session_factory: Callable[[], PyWasmSession] | None = None,
    initial_widgets: Sequence[WasmWidget] | None = None,
    configure_session: Callable[[PyWasmSession], None] | None = None,
    style_template: dict[str, Any] | "StyleTemplate" | None = None,
    assets_route_prefix: str = "/pywasm-assets",
    index_file: str = "index.html",
    pages: dict[str, str] | None = None,
    reserved_paths: Sequence[str] = (),
    spa_fallback: bool = True,
    health_path: str | None = "/health",
    health_payload: Mapping[str, Any] | None = None,
) -> None:
    """Wire a Flask app with a PyWASMui websocket and frontend routes."""

    register_flask_socket(
        sock,
        path=ws_path,
        server_secret=server_secret,
        session_factory=session_factory,
        initial_widgets=initial_widgets,
        configure_session=configure_session,
        style_template=style_template,
    )

    register_flask_packaged_assets(app, route_prefix=assets_route_prefix)

    normalized_health_path: str | None = None
    if health_path:
        normalized_health_path = _normalize_page_route(health_path)
        payload = dict(health_payload or {"status": "ok"})

        @app.get(normalized_health_path)  # type: ignore[attr-defined]
        def _pywasm_health() -> object:
            if jsonify is not None:
                jsonify_fn = cast(Callable[..., object], jsonify)
                return jsonify_fn(payload), 200
            return payload, 200

    frontend_reserved_paths = _merge_reserved_paths(
        reserved_paths,
        ws_path=ws_path,
        health_path=normalized_health_path,
        assets_route_prefix=assets_route_prefix,
    )
    register_flask_frontend(
        app,
        client_root,
        index_file=index_file,
        pages=pages,
        reserved_paths=frontend_reserved_paths,
        spa_fallback=spa_fallback,
    )


class FastAPIAdapter:
    """Object facade for FastAPI integration helpers."""

    def register_frontend_routes(
        self,
        app: object,
        client_root: str | Path,
        *,
        index_file: str = "index.html",
        pages: dict[str, str] | None = None,
        reserved_paths: Sequence[str] = ("ws", "health"),
        spa_fallback: bool = True,
    ) -> None:
        mount_fastapi_frontend(
            app,
            client_root,
            index_file=index_file,
            pages=pages,
            reserved_paths=reserved_paths,
            spa_fallback=spa_fallback,
        )

    def mount_frontend(
        self,
        app: object,
        client_root: str | Path,
        *,
        index_file: str = "index.html",
        pages: dict[str, str] | None = None,
        reserved_paths: Sequence[str] = ("ws", "health"),
        spa_fallback: bool = True,
    ) -> None:
        """Backward-compatible alias of `register_frontend_routes`."""

        self.register_frontend_routes(
            app,
            client_root,
            index_file=index_file,
            pages=pages,
            reserved_paths=reserved_paths,
            spa_fallback=spa_fallback,
        )

    def register_packaged_assets(
        self,
        app: object,
        *,
        route_prefix: str = "/pywasm-assets",
    ) -> Path:
        return mount_fastapi_packaged_assets(app, route_prefix=route_prefix)

    def register_websocket_endpoint(
        self,
        app: object,
        path: str = "/ws",
        server_secret: str = "dev-server-secret-change-me",
        session_factory: Callable[[], PyWasmSession] | None = None,
        initial_widgets: Sequence[WasmWidget] | None = None,
        configure_session: Callable[[PyWasmSession], None] | None = None,
        style_template: dict[str, Any] | "StyleTemplate" | None = None,
    ) -> None:
        mount_fastapi_websocket(
            app,
            path=path,
            server_secret=server_secret,
            session_factory=session_factory,
            initial_widgets=initial_widgets,
            configure_session=configure_session,
            style_template=style_template,
        )

    def mount_socket(
        self,
        app: object,
        path: str = "/ws",
        server_secret: str = "dev-server-secret-change-me",
        session_factory: Callable[[], PyWasmSession] | None = None,
        initial_widgets: Sequence[WasmWidget] | None = None,
        configure_session: Callable[[PyWasmSession], None] | None = None,
        style_template: dict[str, Any] | "StyleTemplate" | None = None,
    ) -> None:
        """Backward-compatible alias of `register_websocket_endpoint`."""

        self.register_websocket_endpoint(
            app,
            path=path,
            server_secret=server_secret,
            session_factory=session_factory,
            initial_widgets=initial_widgets,
            configure_session=configure_session,
            style_template=style_template,
        )

    def mount_websocket(
        self,
        app: object,
        path: str = "/ws",
        server_secret: str = "dev-server-secret-change-me",
        session_factory: Callable[[], PyWasmSession] | None = None,
        initial_widgets: Sequence[WasmWidget] | None = None,
        configure_session: Callable[[PyWasmSession], None] | None = None,
        style_template: dict[str, Any] | "StyleTemplate" | None = None,
    ) -> None:
        self.register_websocket_endpoint(
            app,
            path=path,
            server_secret=server_secret,
            session_factory=session_factory,
            initial_widgets=initial_widgets,
            configure_session=configure_session,
            style_template=style_template,
        )

    def bootstrap_app(
        self,
        app: object,
        client_root: str | Path,
        *,
        ws_path: str = "/ws",
        server_secret: str = "dev-server-secret-change-me",
        session_factory: Callable[[], PyWasmSession] | None = None,
        initial_widgets: Sequence[WasmWidget] | None = None,
        configure_session: Callable[[PyWasmSession], None] | None = None,
        style_template: dict[str, Any] | "StyleTemplate" | None = None,
        assets_route_prefix: str = "/pywasm-assets",
        index_file: str = "index.html",
        pages: dict[str, str] | None = None,
        reserved_paths: Sequence[str] = (),
        spa_fallback: bool = True,
        health_path: str | None = "/health",
        health_payload: Mapping[str, Any] | None = None,
    ) -> None:
        bootstrap_fastapi_app(
            app,
            client_root,
            ws_path=ws_path,
            server_secret=server_secret,
            session_factory=session_factory,
            initial_widgets=initial_widgets,
            configure_session=configure_session,
            style_template=style_template,
            assets_route_prefix=assets_route_prefix,
            index_file=index_file,
            pages=pages,
            reserved_paths=reserved_paths,
            spa_fallback=spa_fallback,
            health_path=health_path,
            health_payload=health_payload,
        )


class FlaskAdapter:
    """Object facade for Flask integration helpers."""

    def register_frontend_routes(
        self,
        app: object,
        client_root: str | Path,
        *,
        index_file: str = "index.html",
        pages: dict[str, str] | None = None,
        reserved_paths: Sequence[str] = ("ws", "health"),
        spa_fallback: bool = True,
    ) -> None:
        register_flask_frontend(
            app,
            client_root,
            index_file=index_file,
            pages=pages,
            reserved_paths=reserved_paths,
            spa_fallback=spa_fallback,
        )

    def mount_frontend(
        self,
        app: object,
        client_root: str | Path,
        *,
        index_file: str = "index.html",
        pages: dict[str, str] | None = None,
        reserved_paths: Sequence[str] = ("ws", "health"),
        spa_fallback: bool = True,
    ) -> None:
        """Backward-compatible alias of `register_frontend_routes`."""

        self.register_frontend_routes(
            app,
            client_root,
            index_file=index_file,
            pages=pages,
            reserved_paths=reserved_paths,
            spa_fallback=spa_fallback,
        )

    def register_packaged_assets(
        self,
        app: object,
        *,
        route_prefix: str = "/pywasm-assets",
    ) -> Path:
        return register_flask_packaged_assets(app, route_prefix=route_prefix)

    def register_websocket_endpoint(
        self,
        sock: object,
        path: str = "/ws",
        server_secret: str = "dev-server-secret-change-me",
        session_factory: Callable[[], PyWasmSession] | None = None,
        initial_widgets: Sequence[WasmWidget] | None = None,
        configure_session: Callable[[PyWasmSession], None] | None = None,
        style_template: dict[str, Any] | "StyleTemplate" | None = None,
    ) -> None:
        register_flask_socket(
            sock,
            path=path,
            server_secret=server_secret,
            session_factory=session_factory,
            initial_widgets=initial_widgets,
            configure_session=configure_session,
            style_template=style_template,
        )

    def mount_socket(
        self,
        sock: object,
        path: str = "/ws",
        server_secret: str = "dev-server-secret-change-me",
        session_factory: Callable[[], PyWasmSession] | None = None,
        initial_widgets: Sequence[WasmWidget] | None = None,
        configure_session: Callable[[PyWasmSession], None] | None = None,
        style_template: dict[str, Any] | "StyleTemplate" | None = None,
    ) -> None:
        """Backward-compatible alias of `register_websocket_endpoint`."""

        self.register_websocket_endpoint(
            sock,
            path=path,
            server_secret=server_secret,
            session_factory=session_factory,
            initial_widgets=initial_widgets,
            configure_session=configure_session,
            style_template=style_template,
        )

    def bootstrap_app(
        self,
        app: object,
        sock: object,
        client_root: str | Path,
        *,
        ws_path: str = "/ws",
        server_secret: str = "dev-server-secret-change-me",
        session_factory: Callable[[], PyWasmSession] | None = None,
        initial_widgets: Sequence[WasmWidget] | None = None,
        configure_session: Callable[[PyWasmSession], None] | None = None,
        style_template: dict[str, Any] | "StyleTemplate" | None = None,
        assets_route_prefix: str = "/pywasm-assets",
        index_file: str = "index.html",
        pages: dict[str, str] | None = None,
        reserved_paths: Sequence[str] = (),
        spa_fallback: bool = True,
        health_path: str | None = "/health",
        health_payload: Mapping[str, Any] | None = None,
    ) -> None:
        bootstrap_flask_app(
            app,
            sock,
            client_root,
            ws_path=ws_path,
            server_secret=server_secret,
            session_factory=session_factory,
            initial_widgets=initial_widgets,
            configure_session=configure_session,
            style_template=style_template,
            assets_route_prefix=assets_route_prefix,
            index_file=index_file,
            pages=pages,
            reserved_paths=reserved_paths,
            spa_fallback=spa_fallback,
            health_path=health_path,
            health_payload=health_payload,
        )


class PyWasmUI:
    """Unified object entrypoint for PyWASMui framework integration."""

    def __init__(self) -> None:
        self.fastapi = FastAPIAdapter()
        self.flask = FlaskAdapter()


pywasm_ui = PyWasmUI()


def mount_fastapi_websocket(
    app: object,
    path: str = "/ws",
    server_secret: str = "dev-server-secret-change-me",
    session_factory: Callable[[], PyWasmSession] | None = None,
    initial_widgets: Sequence[WasmWidget] | None = None,
    configure_session: Callable[[PyWasmSession], None] | None = None,
    style_template: dict[str, Any] | "StyleTemplate" | None = None,
) -> None:
    latency_s = _simulated_latency_seconds()

    factory = session_factory or create_session_factory(
        server_secret,
        initial_widgets=initial_widgets,
        configure_session=configure_session,
        style_template=style_template,
    )
    active_sessions: dict[str, tuple[PyWasmSession, float]] = {}
    ttl_seconds = _session_ttl_seconds()
    max_sessions = _max_active_sessions()
    allowed_origins = _allowed_ws_origins()
    logger.info(
        "Mounting FastAPI websocket endpoint path=%s ttl_seconds=%s max_sessions=%s",
        path,
        ttl_seconds,
        max_sessions,
    )

    @app.websocket(path)  # type: ignore[attr-defined]
    async def _ws_endpoint(websocket: WebSocket) -> None:
        origin = websocket.headers.get("origin")
        if not _is_origin_allowed(origin, allowed_origins):
            logger.warning("WebSocket rejected: origin not allowed (%s)", origin)
            await websocket.close(code=1008, reason="origin-not-allowed")
            return

        await websocket.accept()
        logger.info("WebSocket accepted from origin=%s", origin)
        now = time.time()
        _prune_active_sessions(
            active_sessions,
            now=now,
            ttl_seconds=ttl_seconds,
            max_sessions=max_sessions,
        )
        requested_token = websocket.query_params.get("session_token")
        session_entry = active_sessions.get(requested_token) if requested_token else None
        session = session_entry[0] if session_entry is not None else None
        if session is None:
            session = factory()
            logger.debug("Created new session token=%s", _token_preview(session.session_token))
        else:
            logger.debug("Reusing session token=%s", _token_preview(requested_token))
        active_sessions[session.session_token] = (session, now)

        comm = WasmAppCommunication(
            sender=FastAPIWasmCommandSender(websocket),
            receiver=FastAPIWasmAsyncReceiver(websocket),
        )
        if latency_s > 0:
            await asyncio.sleep(latency_s)
        await comm.send_commands(session.prepare_outbound_commands(session.bootstrap_messages()))

        try:
            async for raw in comm.receive_events():
                if not raw:
                    continue
                if latency_s > 0:
                    await asyncio.sleep(latency_s)
                try:
                    responses = session.handle_client_message(raw)
                except ProtocolViolationError as exc:
                    logger.warning(
                        "Protocol violation token=%s code=%s reason=%s",
                        _token_preview(session.session_token),
                        exc.close_code,
                        exc.reason,
                    )
                    await websocket.close(code=exc.close_code, reason=exc.reason)
                    return
                active_sessions[session.session_token] = (session, time.time())

                if latency_s > 0:
                    await asyncio.sleep(latency_s)
                await comm.send_commands(session.prepare_outbound_commands(responses))
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected token=%s", _token_preview(session.session_token))
            return
        except Exception:
            logger.exception("Unexpected websocket error token=%s", _token_preview(session.session_token))
            raise


def mount_fastapi_socket(
    app: object,
    path: str = "/ws",
    server_secret: str = "dev-server-secret-change-me",
    session_factory: Callable[[], PyWasmSession] | None = None,
    initial_widgets: Sequence[WasmWidget] | None = None,
    configure_session: Callable[[PyWasmSession], None] | None = None,
    style_template: dict[str, Any] | "StyleTemplate" | None = None,
) -> None:
    """Compatibility alias for FastAPI users who prefer `socket` naming."""

    mount_fastapi_websocket(
        app,
        path=path,
        server_secret=server_secret,
        session_factory=session_factory,
        initial_widgets=initial_widgets,
        configure_session=configure_session,
        style_template=style_template,
    )


def register_flask_socket(
    sock: object,
    path: str = "/ws",
    server_secret: str = "dev-server-secret-change-me",
    session_factory: Callable[[], PyWasmSession] | None = None,
    initial_widgets: Sequence[WasmWidget] | None = None,
    configure_session: Callable[[PyWasmSession], None] | None = None,
    style_template: dict[str, Any] | "StyleTemplate" | None = None,
) -> None:
    latency_s = _simulated_latency_seconds()

    factory = session_factory or create_session_factory(
        server_secret,
        initial_widgets=initial_widgets,
        configure_session=configure_session,
        style_template=style_template,
    )
    active_sessions: dict[str, tuple[PyWasmSession, float]] = {}
    ttl_seconds = _session_ttl_seconds()
    max_sessions = _max_active_sessions()
    allowed_origins = _allowed_ws_origins()
    logger.info(
        "Registering Flask socket route path=%s ttl_seconds=%s max_sessions=%s",
        path,
        ttl_seconds,
        max_sessions,
    )

    @sock.route(path)  # type: ignore[attr-defined]
    def _ws_handler(ws: object) -> None:
        origin = None
        environ = getattr(ws, "environ", None)
        if isinstance(environ, dict):
            header_origin = environ.get("HTTP_ORIGIN")
            if isinstance(header_origin, str):
                origin = header_origin
        if not _is_origin_allowed(origin, allowed_origins):
            logger.warning("Flask socket rejected: origin not allowed (%s)", origin)
            return

        now = time.time()
        _prune_active_sessions(
            active_sessions,
            now=now,
            ttl_seconds=ttl_seconds,
            max_sessions=max_sessions,
        )
        requested_token = _extract_flask_requested_token(ws)
        session_entry = active_sessions.get(requested_token) if requested_token else None
        session = session_entry[0] if session_entry is not None else None
        if session is None:
            session = factory()
            logger.debug("Created new Flask session token=%s", _token_preview(session.session_token))
        else:
            logger.debug("Reusing Flask session token=%s", _token_preview(requested_token))
        active_sessions[session.session_token] = (session, now)

        for msg in session.prepare_outbound_commands(session.bootstrap_messages()):
            if latency_s > 0:
                time.sleep(latency_s)
            ws.send(msg)  # type: ignore[attr-defined]

        while True:
            raw = ws.receive()  # type: ignore[attr-defined]
            if raw is None:
                return
            if not raw:
                continue
            if latency_s > 0:
                time.sleep(latency_s)
            try:
                responses = session.handle_client_message(raw)
            except ProtocolViolationError as exc:
                logger.warning(
                    "Flask protocol violation token=%s code=%s reason=%s",
                    _token_preview(session.session_token),
                    exc.close_code,
                    exc.reason,
                )
                # Flask-Sock close semantics can vary by backend; end the loop safely.
                return
            active_sessions[session.session_token] = (session, time.time())
            for response in session.prepare_outbound_commands(responses):
                if latency_s > 0:
                    time.sleep(latency_s)
                ws.send(response)  # type: ignore[attr-defined]
