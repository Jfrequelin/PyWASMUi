from __future__ import annotations

import importlib
import pywasm_ui.widgets.html as html_widgets

from pywasm_ui.widgets import (
    AlertWidget,
    BadgeWidget,
    ButtonWidget,
    CardWidget,
    CheckboxWidget,
    ContainerWidget,
    DatePickerWidget,
    ConnectionStatusWidget,
    DividerWidget,
    HeadingWidget,
    IconButtonWidget,
    LabelWidget,
        ListViewWidget,
    ParagraphWidget,
    ModalWidget,
    OptionWidget,
    ProgressWidget,
    RowWidget,
    SelectWidget,
    SliderWidget,
    StackWidget,
    Style,
    TextAreaWidget,
        TextInputWidget,
    WasmWidget,
        WindowWidget,
    WidgetTree,
)


def test_widget_payload_from_derived_widget() -> None:
    label = LabelWidget(id="label1", parent="root", text="Hello")

    payload = label.to_payload()

    assert payload["id"] == "label1"
    assert payload["kind"] == "Label"
    assert payload["props"]["text"] == "Hello"


def test_widget_tree_upsert_and_lookup() -> None:
    tree = WidgetTree()
    button = ButtonWidget(id="btn1", parent="root", text="Click", classes=["primary"])

    tree.upsert(button)
    payload = tree.as_payload("btn1")

    assert payload is not None
    assert payload["kind"] == "Button"
    assert payload["props"]["text"] == "Click"
    assert payload["props"]["classes"] == ["primary"]


def test_connection_status_widget_patch_updates_state_and_text() -> None:
    status = ConnectionStatusWidget(id="conn1", state="connecting")

    patch = status.update_state_patch("connected")

    assert status.kind == "ConnectionStatus"
    assert patch["id"] == "conn1"
    assert patch["state"] == "connected"
    assert patch["text"] == "Server: connected"


def test_style_object_is_serialized_in_widget_payload() -> None:
    style = Style(font_size="14px", background_color="#0b1220").set("border-radius", "8px")
    label = LabelWidget(id="label_styled", text="Styled", style=style)

    payload = label.to_payload()

    assert payload["props"]["style"]["font-size"] == "14px"
    assert payload["props"]["style"]["background-color"] == "#0b1220"
    assert payload["props"]["style"]["border-radius"] == "8px"


def test_widget_style_proxy_allows_mutation_after_creation() -> None:
    button = ButtonWidget(id="btn_styled", text="Styled")
    button.style.set(font_size="16px", margin_top="6px").set("line-height", "1.3")
    button.style.remove("margin-top")

    payload = button.to_payload()

    assert payload["props"]["style"]["font-size"] == "16px"
    assert payload["props"]["style"]["line-height"] == "1.3"
    assert "margin-top" not in payload["props"]["style"]


def test_style_apply_accepts_css_string_and_dict() -> None:
    style = Style()
    style.apply("color: #111; margin-top: 8px", {"padding_left": "6px"})

    assert style.get("color") == "#111"
    assert style.get("margin-top") == "8px"
    assert style.get("padding-left") == "6px"


def test_widget_style_updates_props_dict_automatically() -> None:
    label = LabelWidget(id="label_auto", text="Auto")

    label.style.set(color="#111111")
    assert label.props["style"]["color"] == "#111111"

    label.style.set("font-size", "15px")
    assert label.props["style"]["font-size"] == "15px"

    label.style.remove("color")
    assert "color" not in label.props["style"]


def test_widget_object_api_supports_text_and_style_attribute_access() -> None:
    label = LabelWidget(id="label_obj", text="Before")

    assert label.text() == "Before"
    label.text("After")
    assert label.text() == "After"

    label.style.margin = "8px"
    label.style.margin_top = "4px"

    payload = label.to_payload()
    assert payload["props"]["text"] == "After"
    assert payload["props"]["style"]["margin"] == "8px"
    assert payload["props"]["style"]["margin-top"] == "4px"


def test_widget_css_and_class_helpers_simplify_styling() -> None:
    button = ButtonWidget(id="btn_css", text="Styled")

    button.css("background-color: #000; color: #fff", border_radius="8px")
    button.add_class("primary", "rounded")
    button.remove_class("rounded")

    payload = button.to_payload()
    assert payload["props"]["style"]["background-color"] == "#000"
    assert payload["props"]["style"]["color"] == "#fff"
    assert payload["props"]["style"]["border-radius"] == "8px"
    assert payload["props"]["classes"] == ["primary"]


def test_new_widget_series_payloads_match_framework_like_conventions() -> None:
    card = CardWidget(id="card1")
    stack = StackWidget(id="stack1")
    row = RowWidget(id="row1")
    heading = HeadingWidget(id="h1", text="Title", level=1)
    paragraph = ParagraphWidget(id="p1", text="Lorem ipsum")
    divider = DividerWidget(id="d1")
    badge = BadgeWidget(id="b1", text="Beta", variant="info")
    alert = AlertWidget(id="a1", text="Saved", level="success")
    slider = SliderWidget(id="s1", value=42, min_value=0, max_value=100, step=2)
    textarea = TextAreaWidget(id="ta1", value="hello")

    assert card.to_payload()["props"]["__tag"] == "div"
    assert stack.to_payload()["props"]["style"]["flex-direction"] == "column"
    assert row.to_payload()["props"]["style"]["display"] == "flex"
    assert heading.to_payload()["props"]["__tag"] == "h1"
    assert paragraph.to_payload()["props"]["text"] == "Lorem ipsum"
    assert divider.to_payload()["props"]["__tag"] == "hr"
    assert "badge-info" in badge.to_payload()["props"]["classes"]
    assert "alert-success" in alert.to_payload()["props"]["classes"]
    assert slider.to_payload()["props"]["input_type"] == "range"
    assert textarea.to_payload()["props"]["__tag"] == "textarea"


def test_icon_button_supports_click_callback_binding() -> None:
    def _noop(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        return None

    button = IconButtonWidget(id="icon_btn", icon="+", text="Add", on_click=_noop)

    handlers = dict(button.iter_event_handlers())
    assert "click" in handlers


def test_widget_convenience_event_methods_bind_handlers() -> None:
    def _noop(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        return None

    button = ButtonWidget(id="btn_click", text="Click me")
    textarea = TextAreaWidget(id="ta_change", value="")

    button.on_click(_noop)
    textarea.on_change(_noop)

    assert "click" in dict(button.iter_event_handlers())
    assert "change" in dict(textarea.iter_event_handlers())


def test_new_form_widgets_payloads_and_handlers() -> None:
    def _noop(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        return None

    date_picker = DatePickerWidget(id="date_1", value="2026-03-08", on_change=_noop)
    checkbox = CheckboxWidget(id="check_1", checked=True, on_change=_noop)
    select = SelectWidget(id="select_1", on_change=_noop)
    option = OptionWidget(id="option_1", parent="select_1", text="Alpha", value="alpha")
    progress = ProgressWidget(id="progress_1", value=25, max_value=120)
    modal = ModalWidget(id="modal_1", text="Details", is_open=True)

    assert date_picker.to_payload()["props"]["input_type"] == "date"
    assert "change" in dict(date_picker.iter_event_handlers())

    checkbox_payload = checkbox.to_payload()["props"]
    assert checkbox_payload["input_type"] == "checkbox"
    assert checkbox_payload["attrs"]["checked"] == "true"

    assert select.to_payload()["props"]["__tag"] == "select"
    assert "change" in dict(select.iter_event_handlers())

    option_payload = option.to_payload()["props"]
    assert option_payload["__tag"] == "option"
    assert option_payload["attrs"]["value"] == "alpha"

    progress_payload = progress.to_payload()["props"]
    assert progress_payload["__tag"] == "progress"
    assert progress_payload["attrs"]["value"] == "25"
    assert progress_payload["attrs"]["max"] == "120"

    modal_payload = modal.to_payload()["props"]
    assert modal_payload["__tag"] == "dialog"
    assert modal_payload["attrs"]["open"] == "true"


def test_html_widget_exports_match_available_widget_classes() -> None:
    exported = set(html_widgets.__all__)
    discovered = {
        name
        for name, value in html_widgets.__dict__.items()
        if name.endswith("Widget")
        and isinstance(value, type)
        and issubclass(value, WasmWidget)
        and value.__module__.startswith("pywasm_ui.widgets.html.")
    }

    assert exported == discovered


def test_html_widget_kinds_follow_class_name_convention() -> None:
    widgets = [
        AlertWidget(id="alert_kind"),
        BadgeWidget(id="badge_kind"),
        ButtonWidget(id="button_kind"),
        CardWidget(id="card_kind"),
        CheckboxWidget(id="checkbox_kind"),
        ContainerWidget(id="container_kind"),
        DatePickerWidget(id="date_kind"),
        DividerWidget(id="divider_kind"),
        HeadingWidget(id="heading_kind"),
        IconButtonWidget(id="icon_button_kind"),
        LabelWidget(id="label_kind"),
        ListViewWidget(id="list_view_kind"),
        ModalWidget(id="modal_kind"),
        OptionWidget(id="option_kind", parent="select_kind", text="Option", value="option"),
        ParagraphWidget(id="paragraph_kind"),
        ProgressWidget(id="progress_kind"),
        RowWidget(id="row_kind"),
        SelectWidget(id="select_kind"),
        SliderWidget(id="slider_kind"),
        StackWidget(id="stack_kind"),
        TextAreaWidget(id="text_area_kind"),
        TextInputWidget(id="text_input_kind"),
        WindowWidget(id="window_kind"),
    ]

    for widget in widgets:
        payload = widget.to_payload()
        expected_kind = widget.__class__.__name__.removesuffix("Widget")
        assert payload["kind"] == expected_kind


def test_legacy_standard_package_import_remains_available() -> None:
    module = importlib.import_module("pywasm_ui.widgets.standard")
    button_cls = getattr(module, "ButtonWidget")

    widget = button_cls(id="legacy_pkg_btn", text="legacy")
    assert widget.to_payload()["kind"] == "Button"


def test_legacy_standard_submodule_import_remains_available() -> None:
    module = importlib.import_module("pywasm_ui.widgets.standard.ButtonWidget")
    button_cls = getattr(module, "ButtonWidget")

    widget = button_cls(id="legacy_submodule_btn", text="legacy")
    assert widget.to_payload()["kind"] == "Button"
