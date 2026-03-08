use crate::models::{ClientState, Widget};
use std::cell::RefCell;

thread_local! {
    static STATE: RefCell<ClientState> = RefCell::new(ClientState::default());
}

pub(crate) fn set_session(token: String, _secret: String) {
    STATE.with(|state| {
        let mut s = state.borrow_mut();
        s.session_token = Some(token);
    });
}

pub(crate) fn next_event_context() -> Option<(String, u64)> {
    STATE.with(|state| {
        let mut s = state.borrow_mut();
        s.nonce = s.nonce.saturating_add(1);
        s.session_token.clone().map(|token| (token, s.nonce))
    })
}

pub(crate) fn upsert_widget(widget: Widget) {
    STATE.with(|state| {
        state.borrow_mut().widgets.insert(widget.id.clone(), widget);
    });
}

pub(crate) fn remove_widget(id: &str) {
    STATE.with(|state| {
        state.borrow_mut().widgets.remove(id);
    });
}
