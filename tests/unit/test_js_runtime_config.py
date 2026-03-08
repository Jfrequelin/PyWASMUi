from __future__ import annotations

import json

from pywasm_ui import JsRuntimeConfig, write_js_runtime_config


def test_js_runtime_config_serialization_and_write(tmp_path) -> None:
    cfg = JsRuntimeConfig(
        ws_host="192.168.1.10",
        ws_port=9000,
        ws_path="/socket",
        ws_protocol="wss",
    )

    as_dict = cfg.to_dict()
    assert as_dict["websocket"]["host"] == "192.168.1.10"
    assert as_dict["websocket"]["port"] == 9000
    assert as_dict["websocket"]["path"] == "/socket"
    assert as_dict["websocket"]["protocol"] == "wss"

    file_path = tmp_path / "config" / "pywasm.runtime.json"
    written = cfg.write_json(file_path)
    loaded = json.loads(written.read_text(encoding="utf-8"))
    assert loaded == as_dict


def test_write_js_runtime_config_helper(tmp_path) -> None:
    file_path = tmp_path / "pywasm.runtime.json"

    written = write_js_runtime_config(file_path, ws_host="10.0.0.2", ws_port=7777)
    loaded = json.loads(written.read_text(encoding="utf-8"))

    assert loaded["websocket"]["host"] == "10.0.0.2"
    assert loaded["websocket"]["port"] == 7777
    assert loaded["websocket"]["path"] == "/ws"
    assert loaded["websocket"]["protocol"] is None
