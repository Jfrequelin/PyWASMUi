from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Sequence, cast
from urllib.parse import parse_qs

from .communication import (
    FastAPIWasmAsyncReceiver,
    FastAPIWasmCommandSender,
    WasmAppCommunication,
)
from .session import ProtocolViolationError, PyWasmSession, create_session_factory
from .widgets import WasmWidget

# Optional framework symbols are initialized here so static analyzers do not
# report them as undefined when imports are unavailable or TYPE_CHECKING is true.
FileResponse = None
JSONResponse = None
jsonify = None
send_from_directory = None

if TYPE_CHECKING:
    from fastapi import WebSocket
    from pywasm_ui.style_template import StyleTemplate
    from fastapi.responses import FileResponse, JSONResponse
    from flask import jsonify, send_from_directory
    from starlette.websockets import WebSocketDisconnect
else:
    try:
        from fastapi import WebSocket
        from fastapi.responses import FileResponse, JSONResponse
        from starlette.websockets import WebSocketDisconnect
    except ImportError:  # pragma: no cover - optional dependency fallback
        WebSocket = Any  # type: ignore[misc,assignment]
        FileResponse = None
        JSONResponse = None

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


def mount_fastapi_frontend(  # pylint: disable=too-many-locals
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
            return file_response(index)
        return json_response(
            status_code=503,
            content={
                "error": "frontend-not-found",
                "hint": f"Missing {root.name}/{index_file}",
            },
        )

    for route, file_path in route_to_file.items():
        if route == "/":
            continue

        async def _page_endpoint(page_file: str = file_path) -> object:
            page = _resolve_static_file(root, page_file)
            if page is None:
                return json_response(
                    status_code=404,
                    content={"error": "page-not-found", "path": page_file},
                )
            return file_response(page)

        app.get(route)(_page_endpoint)  # type: ignore[attr-defined]

    @app.get("/{full_path:path}")  # type: ignore[attr-defined]
    async def _frontend_assets(full_path: str) -> object:
        first_segment = full_path.split("/", 1)[0]
        if first_segment in excluded:
            return json_response(status_code=404, content={"error": "not-found"})

        target = _resolve_static_file(root, full_path)
        if target is not None:
            return file_response(target)

        if spa_fallback:
            index = _resolve_static_file(root, index_file)
            if index is not None:
                return file_response(index)
            return json_response(
                status_code=503,
                content={
                    "error": "frontend-not-found",
                    "hint": f"Missing {root.name}/{index_file}",
                },
            )

        return json_response(status_code=404, content={"error": "not-found"})


def register_flask_frontend(  # pylint: disable=too-many-locals
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
            return send_from_directory_fn(str(root), index_file)
        return (
            jsonify_fn(
                {
                    "error": "frontend-not-found",
                    "hint": f"Missing {root.name}/{index_file}",
                }
            ),
            503,
        )

    for route, file_path in route_to_file.items():
        if route == "/":
            continue

        endpoint_suffix = route.strip("/").replace("/", "_") or "root"
        endpoint_name = f"_frontend_page_{endpoint_suffix}"

        def _page_endpoint(page_file: str = file_path) -> object:
            page = _resolve_static_file(root, page_file)
            if page is None:
                return (
                    jsonify_fn({"error": "page-not-found", "path": page_file}),
                    404,
                )
            return send_from_directory_fn(str(root), page_file)

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
            return jsonify_fn({"error": "not-found"}), 404

        target = _resolve_static_file(root, full_path)
        if target is not None:
            return send_from_directory_fn(str(root), full_path)

        if spa_fallback:
            index = _resolve_static_file(root, index_file)
            if index is not None:
                return send_from_directory_fn(str(root), index_file)
            return (
                jsonify_fn(
                    {
                        "error": "frontend-not-found",
                        "hint": f"Missing {root.name}/{index_file}",
                    }
                ),
                503,
            )

        return jsonify_fn({"error": "not-found"}), 404


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


class PyWasmUI:
    """Unified object entrypoint for pyWasm framework integration."""

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
    active_sessions: dict[str, PyWasmSession] = {}

    @app.websocket(path)  # type: ignore[attr-defined]
    async def _ws_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        requested_token = websocket.query_params.get("session_token")
        session = active_sessions.get(requested_token) if requested_token else None
        if session is None:
            session = factory()
            active_sessions[session.session_token] = session

        comm = WasmAppCommunication(
            sender=FastAPIWasmCommandSender(websocket),
            receiver=FastAPIWasmAsyncReceiver(websocket),
        )
        if latency_s > 0:
            await asyncio.sleep(latency_s)
        await comm.send_commands(session.bootstrap_messages())

        try:
            async for raw in comm.receive_events():
                if not raw:
                    continue
                if latency_s > 0:
                    await asyncio.sleep(latency_s)
                try:
                    responses = session.handle_client_message(raw)
                except ProtocolViolationError as exc:
                    await websocket.close(code=exc.close_code, reason=exc.reason)
                    return

                if latency_s > 0:
                    await asyncio.sleep(latency_s)
                await comm.send_commands(responses)
        except WebSocketDisconnect:
            return


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
    active_sessions: dict[str, PyWasmSession] = {}

    @sock.route(path)  # type: ignore[attr-defined]
    def _ws_handler(ws: object) -> None:
        requested_token = _extract_flask_requested_token(ws)
        session = active_sessions.get(requested_token) if requested_token else None
        if session is None:
            session = factory()
            active_sessions[session.session_token] = session

        for msg in session.bootstrap_messages():
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
            except ProtocolViolationError:
                # Flask-Sock close semantics can vary by backend; end the loop safely.
                return
            for response in responses:
                if latency_s > 0:
                    time.sleep(latency_s)
                ws.send(response)  # type: ignore[attr-defined]
