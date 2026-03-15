use crate::models::{ClientState, Widget};
use serde_json::Value;
use std::cell::RefCell;

thread_local! {
    static STATE: RefCell<ClientState> = RefCell::new(ClientState::default());
}

pub(crate) fn set_session(token: String, secret: String, nonce_seed: u64) {
    STATE.with(|state| {
        let mut s = state.borrow_mut();
        s.session_token = Some(token);
        s.client_secret = Some(secret);
        s.nonce = nonce_seed;
    });
}

pub(crate) fn next_event_context() -> Option<(String, String, u64)> {
    STATE.with(|state| {
        let mut s = state.borrow_mut();
        s.nonce = s.nonce.saturating_add(1);
        match (s.session_token.clone(), s.client_secret.clone()) {
            (Some(token), Some(secret)) => Some((token, secret, s.nonce)),
            _ => None,
        }
    })
}

pub(crate) fn upsert_widget(widget: Widget) {
    STATE.with(|state| {
        state.borrow_mut().widgets.insert(widget.id.clone(), widget);
    });
}

pub(crate) fn set_connection_status(status: &str) {
    STATE.with(|state| {
        state.borrow_mut().connection_status = Some(status.to_string());
    });
}

pub(crate) fn connection_status() -> Option<String> {
    STATE.with(|state| state.borrow().connection_status.clone())
}

pub(crate) fn is_connection_status_widget(widget: &Widget) -> bool {
    widget
        .props
        .get("attrs")
        .and_then(Value::as_object)
        .and_then(|attrs| attrs.get("data-connection-status"))
        .and_then(Value::as_str)
        .map(|value| value == "true")
        .unwrap_or(false)
}

pub(crate) fn remove_widget(id: &str) {
    STATE.with(|state| {
        state.borrow_mut().widgets.remove(id);
    });
}

pub(crate) fn connection_status_widget_ids() -> Vec<String> {
    STATE.with(|state| {
        state
            .borrow()
            .widgets
            .values()
            .filter(|widget| is_connection_status_widget(widget))
            .map(|widget| widget.id.clone())
            .collect()
    })
}
