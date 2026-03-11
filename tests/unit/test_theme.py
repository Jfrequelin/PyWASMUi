from __future__ import annotations

from pywasm_ui import (
    ButtonWidget,
    PyWasmSession,
    SecurityManager,
    ThemeTokens,
    apply_theme,
)


def _new_session() -> PyWasmSession:
    return PyWasmSession(SecurityManager(b"dev-server-secret-change-me"), initial_widgets=[])


def test_apply_theme_sets_button_defaults() -> None:
    session = _new_session()
    apply_theme(session)

    session.create(ButtonWidget(id="btn_theme", text="Theme"))
    widget = session.widget("btn_theme")

    assert widget is not None
    style = widget.props.get("style")
    assert isinstance(style, dict)
    assert style.get("background-color") == "#0ea5e9"
    assert style.get("color") == "#ffffff"


def test_apply_theme_accepts_custom_tokens() -> None:
    session = _new_session()
    apply_theme(
        session,
        ThemeTokens(primary_color="#ff006e", primary_contrast_color="#fefefe"),
    )

    session.create(ButtonWidget(id="btn_custom", text="Custom", classes=["primary"]))
    widget = session.widget("btn_custom")

    assert widget is not None
    style = widget.props.get("style")
    assert isinstance(style, dict)
    assert style.get("background-color") == "#ff006e"
    assert style.get("color") == "#fefefe"


def test_apply_theme_preserves_widget_explicit_style_override() -> None:
    session = _new_session()
    apply_theme(session)

    session.create(
        ButtonWidget(
            id="btn_override",
            text="Override",
            style={"background_color": "#111111"},
        )
    )
    widget = session.widget("btn_override")

    assert widget is not None
    style = widget.props.get("style")
    assert isinstance(style, dict)
    assert style.get("background-color") == "#111111"
