use serde_json::Value;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::{
    window,
    Document,
    Element,
    Event,
    HtmlElement,
    HtmlInputElement,
    HtmlTextAreaElement,
};

use crate::events::send_event;
use crate::models::Widget;

pub(crate) fn ensure_root_widget() {
    let doc = match document() {
        Some(d) => d,
        None => return,
    };

    let app = match doc.get_element_by_id("app") {
        Some(el) => el,
        None => return,
    };

    if doc.get_element_by_id("root").is_none() {
        if let Ok(root) = doc.create_element("div") {
            root.set_id("root");
            let _ = app.append_child(&root);
        }
    }
}

pub(crate) fn update_connection_status_badge(status: &str) {
    ensure_root_widget();
    let doc = match document() {
        Some(d) => d,
        None => return,
    };

    let app = match doc.get_element_by_id("app") {
        Some(el) => el,
        None => return,
    };

    let status_el = match doc.get_element_by_id("ws-status") {
        Some(el) => el,
        None => {
            let created = match doc.create_element("p") {
                Ok(el) => el,
                Err(_) => return,
            };
            created.set_id("ws-status");
            let _ = app.prepend_with_node_1(&created);
            created
        }
    };

    let label = match status {
        "connected" => "Server: connected",
        "connecting" => "Server: connecting...",
        "error" => "Server: connection error",
        "closed" => "Server: disconnected",
        _ => "Server: unknown",
    };

    status_el.set_text_content(Some(label));
    let _ = status_el.set_attribute("class", &format!("ws-status ws-{}", status));
}

pub(crate) fn render_widget(widget: &Widget) {
    let doc = match document() {
        Some(d) => d,
        None => return,
    };

    let parent = doc
        .get_element_by_id(&widget.parent)
        .or_else(|| doc.get_element_by_id("root"));

    let Some(parent_el) = parent else {
        return;
    };

    if doc.get_element_by_id(&widget.id).is_some() {
        return;
    }

    let element = create_widget_from_props(&doc, widget);

    if let Some(el) = element {
        let _ = parent_el.append_child(&el);
    }
}

pub(crate) fn apply_update_patch(patch: Value) {
    let id = match patch.get("id").and_then(Value::as_str) {
        Some(v) => v,
        None => return,
    };

    let doc = match document() {
        Some(d) => d,
        None => return,
    };
    let Some(el) = doc.get_element_by_id(id) else {
        return;
    };

    if let Some(text) = patch.get("text").and_then(Value::as_str) {
        el.set_text_content(Some(text));
    }

    if let Some(value) = patch.get("value").and_then(Value::as_str) {
        if let Ok(input) = el.clone().dyn_into::<HtmlInputElement>() {
            input.set_value(value);
        } else if let Ok(textarea) = el.clone().dyn_into::<HtmlTextAreaElement>() {
            textarea.set_value(value);
        }
    }

    if let Some(enabled) = patch.get("enabled").and_then(Value::as_bool) {
        if enabled {
            let _ = el.remove_attribute("disabled");
        } else {
            let _ = el.set_attribute("disabled", "true");
        }
    }

    if let Some(classes) = patch.get("classes").and_then(Value::as_array) {
        let class_list = classes
            .iter()
            .filter_map(Value::as_str)
            .collect::<Vec<_>>()
            .join(" ");
        let _ = el.set_attribute("class", &class_list);
    }

    if let Some(style) = patch.get("style").and_then(Value::as_object) {
        apply_style_object(&el, style);
    }

    if let Some(attrs) = patch.get("attrs").and_then(Value::as_object) {
        for (key, value) in attrs {
            if let Some(text) = value.as_str() {
                let _ = el.set_attribute(key, text);
            } else if let Some(number) = value.as_f64() {
                let _ = el.set_attribute(key, &number.to_string());
            } else if let Some(boolean) = value.as_bool() {
                let _ = el.set_attribute(key, if boolean { "true" } else { "false" });
            }
        }
    }

    if let Some(remove_attrs) = patch.get("remove_attrs").and_then(Value::as_array) {
        for attr in remove_attrs.iter().filter_map(Value::as_str) {
            let _ = el.remove_attribute(attr);
        }
    }
}

pub(crate) fn remove_element(id: &str) {
    if let Some(doc) = document() {
        if let Some(el) = doc.get_element_by_id(id) {
            el.remove();
        }
    }
}

fn create_widget_from_props(doc: &Document, widget: &Widget) -> Option<Element> {
    let tag = widget
        .props
        .get("__tag")
        .and_then(Value::as_str)
        .unwrap_or("div");
    let text_prop = widget.props.get("__text_prop").and_then(Value::as_str);

    let el = create_widget_element(doc, widget, tag, text_prop)?;
    apply_common_attributes(&el, widget);
    apply_input_specific_attributes(&el, widget, tag);
    bind_server_declared_event(&el, widget, tag);
    Some(el)
}

fn apply_common_attributes(el: &Element, widget: &Widget) {
    if let Some(enabled) = widget.props.get("enabled").and_then(Value::as_bool) {
        if enabled {
            let _ = el.remove_attribute("disabled");
        } else {
            let _ = el.set_attribute("disabled", "true");
        }
    }

    if let Some(classes) = widget.props.get("classes").and_then(Value::as_array) {
        let class_list = classes
            .iter()
            .filter_map(Value::as_str)
            .collect::<Vec<_>>()
            .join(" ");
        let _ = el.set_attribute("class", &class_list);
    }

    if let Some(style) = widget.props.get("style").and_then(Value::as_object) {
        apply_style_object(el, style);
    }

    if let Some(attrs) = widget.props.get("attrs").and_then(Value::as_object) {
        for (key, value) in attrs {
            if let Some(text) = value.as_str() {
                let _ = el.set_attribute(key, text);
            } else if let Some(number) = value.as_f64() {
                let _ = el.set_attribute(key, &number.to_string());
            } else if let Some(boolean) = value.as_bool() {
                let _ = el.set_attribute(key, if boolean { "true" } else { "false" });
            }
        }
    }

    if let Some(pending_class) = widget.props.get("__pending_class").and_then(Value::as_str) {
        let _ = el.set_attribute("data-pending-class", pending_class);
    }
}

fn apply_style_object(el: &Element, style: &serde_json::Map<String, Value>) {
    let Ok(html_el) = el.clone().dyn_into::<HtmlElement>() else {
        return;
    };

    for (name, value) in style {
        if value.is_null() {
            let _ = html_el.style().remove_property(name);
            continue;
        }

        if let Some(as_text) = value.as_str() {
            let _ = html_el.style().set_property(name, as_text);
            continue;
        }

        if let Some(as_bool) = value.as_bool() {
            let _ = html_el
                .style()
                .set_property(name, if as_bool { "true" } else { "false" });
            continue;
        }

        if let Some(as_number) = value.as_f64() {
            let _ = html_el.style().set_property(name, &as_number.to_string());
        }
    }
}

fn apply_input_specific_attributes(el: &Element, widget: &Widget, tag: &str) {
    if tag != "input" {
        return;
    }

    let input_type = widget
        .props
        .get("input_type")
        .and_then(Value::as_str)
        .unwrap_or("text");
    let _ = el.set_attribute("type", input_type);

    if let Some(value) = widget.props.get("value").and_then(Value::as_str) {
        if let Ok(input) = el.clone().dyn_into::<HtmlInputElement>() {
            input.set_value(value);
        }
    }
}

fn bind_server_declared_event(el: &Element, widget: &Widget, tag: &str) {
    let Some(event_kind) = widget.props.get("__event").and_then(Value::as_str) else {
        return;
    };

    let widget_id = widget.id.clone();
    let event_name = event_kind.to_string();
    let tag_name = tag.to_string();
    let el_for_cb = el.clone();
    let is_input_change = (tag == "input" || tag == "textarea") && event_kind == "change";

    let handler = Closure::<dyn FnMut(Event)>::new(move |_event: Event| {
        let value = if is_input_change {
            if tag_name == "input" {
                el_for_cb
                    .clone()
                    .dyn_into::<HtmlInputElement>()
                    .ok()
                    .map(|i| i.value())
            } else {
                el_for_cb
                    .clone()
                    .dyn_into::<HtmlTextAreaElement>()
                    .ok()
                    .map(|t| t.value())
            }
        } else {
            None
        };
        send_event(&event_name, &widget_id, value);
    });
    let _ = el.add_event_listener_with_callback(event_kind, handler.as_ref().unchecked_ref());
    handler.forget();
}

fn create_widget_element(
    doc: &Document,
    widget: &Widget,
    tag_name: &str,
    text_prop_key: Option<&str>,
) -> Option<Element> {
    let el = doc.create_element(tag_name).ok()?;
    el.set_id(&widget.id);
    if let Some(key) = text_prop_key {
        if let Some(text) = widget.props.get(key).and_then(Value::as_str) {
            el.set_text_content(Some(text));
        }
    }
    Some(el)
}

fn document() -> Option<Document> {
    window().and_then(|w| w.document())
}
