from __future__ import annotations

from pywasm_ui import (
    ButtonWidget,
    CardWidget,
    Component,
    LabelWidget,
    PyWasmSession,
    SecurityManager,
    render_component_widgets,
)


class GreetingComponent(Component):
    def build(self, session: PyWasmSession):
        count = int(session.data.get("count", 0))
        return [
            CardWidget(id="card_root", parent="root"),
            LabelWidget(id="greeting_label", parent="card_root", text=f"Hello #{count}"),
            ButtonWidget(id="greeting_button", parent="card_root", text="Increment"),
        ]


class NestedComponent(Component):
    def __init__(self, child: Component) -> None:
        self.child = child

    def build(self, session: PyWasmSession):
        return [self.child]


def _new_session() -> PyWasmSession:
    return PyWasmSession(SecurityManager(b"dev-server-secret-change-me"), initial_widgets=[])


def test_render_component_widgets_flattens_nested_components() -> None:
    session = _new_session()
    widgets = render_component_widgets(NestedComponent(GreetingComponent()), session)

    assert [w.id for w in widgets] == ["card_root", "greeting_label", "greeting_button"]


def test_session_create_component_creates_all_widgets() -> None:
    session = _new_session()
    session.data["count"] = 2

    messages = session.create_component(GreetingComponent())

    assert len(messages) == 3
    assert all(msg.type == "create" for msg in messages)

    payload = session.widget("greeting_label")
    assert payload is not None
    assert payload.props.get("text") == "Hello #2"
