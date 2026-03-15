from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class JsRuntimeConfig:
    ws_host: str | None = None
    ws_port: int | None = None
    ws_path: str = "/ws"
    ws_protocol: str | None = None
    mount_element_id: str = "app"
    shared: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "websocket": {
                "host": self.ws_host,
                "port": self.ws_port,
                "path": self.ws_path,
                "protocol": self.ws_protocol,
            },
            "mount": {
                "elementId": self.mount_element_id,
            },
            "shared": self.shared,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, indent=indent) + "\n"

    def write_json(self, file_path: str | Path) -> Path:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path


def write_js_runtime_config(
    file_path: str | Path,
    ws_host: str | None = None,
    ws_port: int | None = None,
    ws_path: str = "/ws",
    ws_protocol: str | None = None,
    mount_element_id: str = "app",
    shared: dict[str, Any] | None = None,
) -> Path:
    cfg = JsRuntimeConfig(
        ws_host=ws_host,
        ws_port=ws_port,
        ws_path=ws_path,
        ws_protocol=ws_protocol,
        mount_element_id=mount_element_id,
        shared=shared or {},
    )
    return cfg.write_json(file_path)


def render_embed_snippet(
    ws_path: str = "/ws",
    *,
    mount_element_id: str = "app",
    script_src: str = "/src/main.js",
    ws_host: str | None = None,
    ws_port: int | None = None,
    ws_protocol: str | None = None,
    shared: dict[str, Any] | None = None,
) -> str:
    """Return an embeddable HTML snippet for Jinja2 templates.

    This lets users keep their own page/layout and inject PyWASMui with one div
    plus a module script.
    """

    cfg = JsRuntimeConfig(
        ws_host=ws_host,
        ws_port=ws_port,
        ws_path=ws_path,
        ws_protocol=ws_protocol,
        mount_element_id=mount_element_id,
        shared=shared or {},
    ).to_dict()
    cfg_json = json.dumps(cfg, ensure_ascii=True)

    return (
        f'<div id="{mount_element_id}" data-pywasm-root="true"></div>\n'
        f"<script>window.__PYWASM_RUNTIME_CONFIG__ = {cfg_json};</script>\n"
        f'<script type="module" src="{script_src}"></script>'
    )
