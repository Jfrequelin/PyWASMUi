use serde_json::Value;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::{
    window,
    AddEventListenerOptions,
    Document,
    Element,
    Event,
    HtmlElement,
    HtmlInputElement,
    HtmlSelectElement,
    HtmlTextAreaElement,
};

use crate::events::send_event;
use crate::models::Widget;
use crate::state;

const SVG_NS: &str = "http://www.w3.org/2000/svg";

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
    let label = match status {
        "connected" => "Server: connected",
        "connecting" => "Server: connecting...",
        "error" => "Server: connection error",
        "closed" => "Server: disconnected",
        _ => "Server: unknown",
    };

    let widget_ids = state::connection_status_widget_ids();
    for widget_id in widget_ids {
        let patch = serde_json::json!({
            "id": widget_id,
            "text": label,
            "attrs": {"data-connection-state": status},
        });
        apply_update_patch(patch);
    }
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

    render_bar_chart_if_needed(&el);
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
    bind_server_declared_events(&el, widget, tag);
    render_special_content(doc, &el, widget);
    Some(el)
}

fn render_special_content(doc: &Document, el: &Element, widget: &Widget) {
    if widget.kind == "BarChart" || has_css_class(el, "bar-chart-widget") {
        render_bar_chart(doc, el);
    }
}

fn render_bar_chart_if_needed(el: &Element) {
    if !has_css_class(el, "bar-chart-widget") {
        return;
    }
    let Some(doc) = document() else {
        return;
    };
    render_bar_chart(&doc, el);
}

fn render_bar_chart(doc: &Document, host: &Element) {
    while let Some(child) = host.first_child() {
        let _ = host.remove_child(&child);
    }

    let values = parse_number_array_attr(host, "data-chart-values");
    if values.is_empty() {
        host.set_text_content(Some("No chart data"));
        return;
    }

    let labels = parse_string_array_attr(host, "data-chart-labels");
    let width = parse_f64_attr(host, "data-chart-width").unwrap_or(360.0).max(120.0);
    let height = parse_f64_attr(host, "data-chart-height").unwrap_or(180.0).max(120.0);
    let computed_max = values.iter().copied().reduce(f64::max).unwrap_or(1.0).max(1.0);
    let max_value = parse_f64_attr(host, "data-chart-max").unwrap_or(computed_max).max(1.0);

    let Some(svg) = doc.create_element_ns(Some(SVG_NS), "svg").ok() else {
        return;
    };
    let _ = svg.set_attribute("viewBox", &format!("0 0 {} {}", width, height));
    let _ = svg.set_attribute("aria-hidden", "true");

    let margin_left = 30.0;
    let margin_right = 12.0;
    let margin_top = 12.0;
    let margin_bottom = 28.0;

    let chart_w = (width - margin_left - margin_right).max(16.0);
    let chart_h = (height - margin_top - margin_bottom).max(16.0);

    if let Ok(axis) = doc.create_element_ns(Some(SVG_NS), "line") {
        let _ = axis.set_attribute("x1", &margin_left.to_string());
        let _ = axis.set_attribute("y1", &(margin_top + chart_h).to_string());
        let _ = axis.set_attribute("x2", &(margin_left + chart_w).to_string());
        let _ = axis.set_attribute("y2", &(margin_top + chart_h).to_string());
        let _ = axis.set_attribute("stroke", "#94a3b8");
        let _ = axis.set_attribute("stroke-width", "1");
        let _ = svg.append_child(&axis);
    }

    let count = values.len() as f64;
    let slot_w = chart_w / count;
    let bar_w = (slot_w * 0.64).max(8.0);

    for (idx, value) in values.iter().enumerate() {
        let clamped = value.max(0.0);
        let ratio = (clamped / max_value).min(1.0);
        let bar_h = (ratio * chart_h).max(1.0);
        let x = margin_left + (idx as f64 * slot_w) + ((slot_w - bar_w) / 2.0);
        let y = margin_top + chart_h - bar_h;

        if let Ok(rect) = doc.create_element_ns(Some(SVG_NS), "rect") {
            let _ = rect.set_attribute("x", &format!("{:.2}", x));
            let _ = rect.set_attribute("y", &format!("{:.2}", y));
            let _ = rect.set_attribute("width", &format!("{:.2}", bar_w));
            let _ = rect.set_attribute("height", &format!("{:.2}", bar_h));
            let _ = rect.set_attribute("rx", "4");
            let _ = rect.set_attribute("fill", "#0f766e");
            let _ = svg.append_child(&rect);
        }

        if let Ok(text_value) = doc.create_element_ns(Some(SVG_NS), "text") {
            let _ = text_value.set_attribute("x", &format!("{:.2}", x + (bar_w / 2.0)));
            let _ = text_value.set_attribute("y", &format!("{:.2}", (y - 4.0).max(10.0)));
            let _ = text_value.set_attribute("font-size", "10");
            let _ = text_value.set_attribute("text-anchor", "middle");
            let _ = text_value.set_attribute("fill", "#334155");
            text_value.set_text_content(Some(&format!("{:.0}", clamped)));
            let _ = svg.append_child(&text_value);
        }

        if let Some(label) = labels.get(idx) {
            if let Ok(text_label) = doc.create_element_ns(Some(SVG_NS), "text") {
                let _ = text_label.set_attribute("x", &format!("{:.2}", x + (bar_w / 2.0)));
                let _ = text_label.set_attribute("y", &format!("{:.2}", margin_top + chart_h + 14.0));
                let _ = text_label.set_attribute("font-size", "10");
                let _ = text_label.set_attribute("text-anchor", "middle");
                let _ = text_label.set_attribute("fill", "#64748b");
                text_label.set_text_content(Some(label));
                let _ = svg.append_child(&text_label);
            }
        }
    }

    let _ = host.append_child(&svg);
}

fn parse_number_array_attr(el: &Element, name: &str) -> Vec<f64> {
    let Some(raw) = el.get_attribute(name) else {
        return Vec::new();
    };
    let Ok(parsed) = serde_json::from_str::<Vec<Value>>(&raw) else {
        return Vec::new();
    };
    parsed.iter().filter_map(Value::as_f64).collect()
}

fn parse_string_array_attr(el: &Element, name: &str) -> Vec<String> {
    let Some(raw) = el.get_attribute(name) else {
        return Vec::new();
    };
    let Ok(parsed) = serde_json::from_str::<Vec<String>>(&raw) else {
        return Vec::new();
    };
    parsed
}

fn parse_f64_attr(el: &Element, name: &str) -> Option<f64> {
    let raw = el.get_attribute(name)?;
    raw.parse::<f64>().ok()
}

fn has_css_class(el: &Element, class_name: &str) -> bool {
    let Some(classes) = el.get_attribute("class") else {
        return false;
    };
    classes.split_whitespace().any(|name| name == class_name)
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

fn bind_server_declared_events(el: &Element, widget: &Widget, tag: &str) {
    let mut event_names: Vec<String> = Vec::new();

    if let Some(events) = widget.props.get("__events").and_then(Value::as_array) {
        for event_name in events.iter().filter_map(Value::as_str) {
            if !event_name.is_empty() && !event_names.iter().any(|existing| existing == event_name) {
                event_names.push(event_name.to_string());
            }
        }
    }

    if let Some(single) = widget.props.get("__event").and_then(Value::as_str) {
        if !single.is_empty() && !event_names.iter().any(|existing| existing == single) {
            event_names.push(single.to_string());
        }
    }

    if event_names.is_empty() {
        return;
    }

    for event_name in event_names {
        let widget_id = widget.id.clone();
        let tag_name = tag.to_string();
        let event_name_for_cb = event_name.clone();
        let el_for_cb = el.clone();

        let handler = Closure::<dyn FnMut(Event)>::new(move |_event: Event| {
            let value = event_value_for(&el_for_cb, &tag_name, &event_name_for_cb);
            send_event(&event_name_for_cb, &widget_id, value);
        });
        if is_passive_scroll_event(&event_name) {
            let options = AddEventListenerOptions::new();
            options.set_passive(true);
            let _ = el.add_event_listener_with_callback_and_add_event_listener_options(
                &event_name,
                handler.as_ref().unchecked_ref(),
                &options,
            );
        } else {
            let _ = el.add_event_listener_with_callback(&event_name, handler.as_ref().unchecked_ref());
        }
        handler.forget();
    }
}

fn is_passive_scroll_event(event_name: &str) -> bool {
    matches!(event_name, "wheel" | "touchstart" | "touchmove")
}

fn event_value_for(el: &Element, tag: &str, event_kind: &str) -> Option<String> {
    if event_kind != "change" && event_kind != "input" {
        return None;
    }

    if tag == "input" {
        let input = el.clone().dyn_into::<HtmlInputElement>().ok()?;
        let input_type = input.type_();
        if input_type == "checkbox" || input_type == "radio" {
            return Some(if input.checked() { "true".to_string() } else { "false".to_string() });
        }
        return Some(input.value());
    }

    if tag == "textarea" {
        return el
            .clone()
            .dyn_into::<HtmlTextAreaElement>()
            .ok()
            .map(|textarea| textarea.value());
    }

    if tag == "select" {
        return el
            .clone()
            .dyn_into::<HtmlSelectElement>()
            .ok()
            .map(|select| select.value());
    }

    None
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
