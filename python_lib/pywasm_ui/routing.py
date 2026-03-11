from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Sequence

if TYPE_CHECKING:
    from flask import Flask
    from fastapi import FastAPI
    from starlette.requests import Request


FastAPIGuard = Callable[["Request"], bool]
FlaskGuard = Callable[[Any], bool]


@dataclass(frozen=True)
class PageDefinition:
    """Simple page declaration for lightweight Python-side routing."""

    path: str
    template: str
    guard: FastAPIGuard | FlaskGuard | None = None


def page(
    path: str,
    template: str,
    *,
    guard: FastAPIGuard | FlaskGuard | None = None,
) -> PageDefinition:
    """Create a page definition with an optional guard callback."""

    normalized = path if path.startswith("/") else f"/{path}"
    return PageDefinition(path=normalized, template=template, guard=guard)


def register_fastapi_pages(app: "FastAPI", web_root: Path, pages: Sequence[PageDefinition]) -> None:
    """Register static HTML pages with optional per-page guards on FastAPI."""

    try:
        from fastapi import HTTPException
        from fastapi.responses import FileResponse
        from starlette.requests import Request as StarletteRequest
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("FastAPI response classes are unavailable") from exc

    root = web_root.resolve()

    def _make_fastapi_handler(target: Path, guard: FastAPIGuard | None):
        async def _handler(request: StarletteRequest):
            if guard is not None and not guard(request):
                raise HTTPException(status_code=403, detail="Forbidden")
            return FileResponse(target)

        return _handler

    for index, definition in enumerate(pages):
        target = (root / definition.template).resolve()
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"missing page template: {target}")

        guard = definition.guard if callable(definition.guard) else None
        _handler = _make_fastapi_handler(target, guard)  # type: ignore[arg-type]

        _handler.__name__ = (
            f"pywasm_page_{index}_{definition.path.strip('/').replace('/', '_') or 'root'}"
        )
        app.get(definition.path)(_handler)


def register_flask_pages(app: "Flask", web_root: Path, pages: Sequence[PageDefinition]) -> None:
    """Register static HTML pages with optional per-page guards on Flask."""

    try:
        from flask import abort, request as flask_request, send_from_directory
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Flask response helpers are unavailable") from exc

    root = web_root.resolve()

    def _make_flask_handler(template: str, guard: FlaskGuard | None):
        def _handler():
            if guard is not None and not guard(flask_request):
                abort(403)
            return send_from_directory(root, template)

        return _handler

    for index, definition in enumerate(pages):
        target = (root / definition.template).resolve()
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"missing page template: {target}")

        route_path = definition.path
        endpoint = f"pywasm_page_{index}_{route_path.strip('/').replace('/', '_') or 'root'}"

        guard = definition.guard if callable(definition.guard) else None
        _handler = _make_flask_handler(definition.template, guard)  # type: ignore[arg-type]

        app.add_url_rule(route_path, endpoint=endpoint, view_func=_handler)
