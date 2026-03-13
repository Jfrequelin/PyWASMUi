use crate::dom;
use crate::models::{IncomingMessage, InitPayload};
use crate::state;

pub(crate) fn handle_server_message(message: &str) {
    if let Ok(init) = serde_json::from_str::<InitPayload>(message) {
        if init.protocol == 1 && init.r#type == "init" {
            state::set_session(init.session.token, init.client_secret);
        }
        return;
    }

    let parsed = match serde_json::from_str::<IncomingMessage>(message) {
        Ok(m) if m.protocol == 1 => m,
        _ => return,
    };

    match parsed.r#type.as_str() {
        "create" => {
            if let Some(widget) = parsed.widget {
                let is_connection_status = state::is_connection_status_widget(&widget);
                state::upsert_widget(widget.clone());
                dom::render_widget(&widget);
                if is_connection_status {
                    if let Some(status) = state::connection_status() {
                        dom::update_connection_status_badge(&status);
                    }
                }
            }
        }
        "update" => {
            if let Some(patch) = parsed.patch {
                dom::apply_update_patch(patch);
            }
        }
        "delete" => {
            if let Some(widget) = parsed.widget {
                dom::remove_element(&widget.id);
                state::remove_widget(&widget.id);
            }
        }
        _ => {}
    }
}
