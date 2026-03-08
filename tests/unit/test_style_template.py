from __future__ import annotations

import json

from pywasm_ui import ButtonWidget, LabelWidget, PyWasmSession, StyleTemplate
from pywasm_ui.security import SecurityManager
from pywasm_ui.session import create_session_factory


def test_style_template_save_and_load_roundtrip(tmp_path) -> None:  # type: ignore[no-untyped-def]
    template = (
        StyleTemplate()
        .set_kind("Label", "color: #111")
        .set_class("primary", {"border_radius": "8px"})
    )

    target = tmp_path / "theme.json"
    template.save(target)

    loaded = StyleTemplate.load(target)
    assert loaded.by_kind["Label"]["color"] == "#111"
    assert loaded.by_class["primary"]["border-radius"] == "8px"

    raw = json.loads(target.read_text(encoding="utf-8"))
    assert "by_kind" in raw
    assert "by_class" in raw


def test_template_applies_cascading_defaults_with_widget_override() -> None:
    session = PyWasmSession(
        SecurityManager(server_secret=b"test-server-secret"),
        initial_widgets=[
            LabelWidget(id="l1", parent="root", text="x", style={"color": "#f00"}),
            ButtonWidget(id="b1", parent="root", text="Go", classes=["primary"]),
        ],
    )
    session.set_default_style_for_kind("Label", {"font_size": "14px", "color": "#111"})
    session.set_default_style_for_class(
        "primary",
        {"padding": "10px", "background_color": "#0ea5e9"},
    )

    messages = [json.loads(msg) for msg in session.bootstrap_messages()]
    creates = [m for m in messages if m.get("type") == "create"]

    label_payload = next(m for m in creates if m["widget"]["id"] == "l1")
    button_payload = next(m for m in creates if m["widget"]["id"] == "b1")

    assert label_payload["widget"]["props"]["style"]["font-size"] == "14px"
    assert label_payload["widget"]["props"]["style"]["color"] == "#f00"
    assert button_payload["widget"]["props"]["style"]["padding"] == "10px"
    assert button_payload["widget"]["props"]["style"]["background-color"] == "#0ea5e9"


def test_factory_applies_template_to_each_session() -> None:
    factory = create_session_factory(
        "test-server-secret",
        initial_widgets=[LabelWidget(id="l1", parent="root", text="x")],
        style_template=StyleTemplate(by_kind={"Label": {"color": "#333"}}),
    )

    first = factory()
    second = factory()

    first_bootstrap = [json.loads(msg) for msg in first.bootstrap_messages()]
    second_bootstrap = [json.loads(msg) for msg in second.bootstrap_messages()]

    for boot in (first_bootstrap, second_bootstrap):
        create = next(m for m in boot if m.get("type") == "create" and m["widget"]["id"] == "l1")
        assert create["widget"]["props"]["style"]["color"] == "#333"
