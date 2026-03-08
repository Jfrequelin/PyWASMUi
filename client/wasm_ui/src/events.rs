use serde_json::json;

use crate::models::EventBody;
use crate::state;
use crate::transport::ws_send;

pub(crate) fn send_event(kind: &str, id: &str, value: Option<String>) {
    let Some((session_token, nonce)) = state::next_event_context() else {
        return;
    };

    let event = EventBody {
        kind,
        id,
        value,
        nonce: Some(nonce),
    };

    let payload = json!({
        "protocol": 1,
        "type": "event",
        "session": {"token": session_token},
        "event": event
    });

    if let Ok(raw) = serde_json::to_string(&payload) {
        ws_send(&raw);
    }
}
