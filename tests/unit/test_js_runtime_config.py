from __future__ import annotations

import json
import re

from pywasm_ui import JsRuntimeConfig, render_embed_snippet, write_js_runtime_config


def test_js_runtime_config_serialization_and_write(tmp_path) -> None:
    cfg = JsRuntimeConfig(
        ws_host="192.168.1.10",
        ws_port=9000,
        ws_path="/socket",
        ws_protocol="wss",
        shared={"chart": {"labels": ["A", "B"], "values": [1, 2]}},
    )

    as_dict = cfg.to_dict()
    assert as_dict["websocket"]["host"] == "192.168.1.10"
    assert as_dict["websocket"]["port"] == 9000
    assert as_dict["websocket"]["path"] == "/socket"
    assert as_dict["websocket"]["protocol"] == "wss"
    assert as_dict["shared"]["chart"]["labels"] == ["A", "B"]

    file_path = tmp_path / "config" / "pywasm.runtime.json"
    written = cfg.write_json(file_path)
    loaded = json.loads(written.read_text(encoding="utf-8"))
    assert loaded == as_dict


def test_write_js_runtime_config_helper(tmp_path) -> None:
    file_path = tmp_path / "pywasm.runtime.json"

    written = write_js_runtime_config(
        file_path,
        ws_host="10.0.0.2",
        ws_port=7777,
        shared={"series": [3, 5, 8]},
    )
    loaded = json.loads(written.read_text(encoding="utf-8"))

    assert loaded["websocket"]["host"] == "10.0.0.2"
    assert loaded["websocket"]["port"] == 7777
    assert loaded["websocket"]["path"] == "/ws"
    assert loaded["websocket"]["protocol"] is None
    assert loaded["shared"]["series"] == [3, 5, 8]


def test_render_embed_snippet_includes_shared_runtime_variables() -> None:
    snippet = render_embed_snippet(
        ws_path="/ws",
        shared={"chartData": [10, 20, 30], "title": "Revenue"},
    )

    match = re.search(r"window\.__PYWASM_RUNTIME_CONFIG__\s*=\s*(\{.*\});", snippet)
    assert match is not None

    runtime_cfg = json.loads(match.group(1))
    assert runtime_cfg["websocket"]["path"] == "/ws"
    assert runtime_cfg["shared"]["chartData"] == [10, 20, 30]
    assert runtime_cfg["shared"]["title"] == "Revenue"
