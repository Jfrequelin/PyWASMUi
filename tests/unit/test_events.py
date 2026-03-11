from __future__ import annotations

from pywasm_ui import (
    ChangeEvent,
    ClickEvent,
    PyWasmSession,
    SecurityManager,
    SliderChangeEvent,
    TextInputChangeEvent,
    to_typed_event,
)
from pywasm_ui.protocol import EventPayload


def _new_session() -> PyWasmSession:
    return PyWasmSession(SecurityManager(b"dev-server-secret-change-me"), initial_widgets=[])


def test_to_typed_event_maps_click() -> None:
    event = to_typed_event(EventPayload(kind="click", id="btn1", value=None, nonce=3))

    assert isinstance(event, ClickEvent)
    assert event.widget_id == "btn1"
    assert event.nonce == 3


def test_to_typed_event_maps_change_string_and_numeric() -> None:
    text_event = to_typed_event(EventPayload(kind="change", id="input1", value="abc"))
    slider_event = to_typed_event(EventPayload(kind="change", id="slider1", value=42))

    assert isinstance(text_event, TextInputChangeEvent)
    assert text_event.text == "abc"

    assert isinstance(slider_event, SliderChangeEvent)
    assert slider_event.number == 42.0


def test_register_typed_event_handler_wraps_payload() -> None:
    session = _new_session()
    seen: list[ChangeEvent] = []

    def on_change(_session: PyWasmSession, event: ChangeEvent):
        seen.append(event)

    session.register_typed_event_handler("change", "input1", on_change)
    handler = session._event_handlers[("change", "input1")]
    handler(session, EventPayload(kind="change", id="input1", value="hello"))

    assert len(seen) == 1
    assert isinstance(seen[0], TextInputChangeEvent)
    assert seen[0].widget_id == "input1"


def test_on_click_typed_maps_to_click_event() -> None:
    session = _new_session()
    seen: list[ClickEvent] = []

    def on_click(_session: PyWasmSession, event: ClickEvent):
        seen.append(event)

    session.on_click_typed("btn1", on_click)
    handler = session._event_handlers[("click", "btn1")]
    handler(session, EventPayload(kind="click", id="btn1", value=None, nonce=7))

    assert len(seen) == 1
    assert isinstance(seen[0], ClickEvent)
    assert seen[0].widget_id == "btn1"
    assert seen[0].nonce == 7
