use base64::Engine;
use hmac::{Hmac, Mac};
use serde_json::json;
use sha2::Sha256;

use crate::models::EventBody;
use crate::state;
use crate::transport::ws_send;

type HmacSha256 = Hmac<Sha256>;

fn sign_event(event: &EventBody, client_secret: &str) -> Option<String> {
    let canonical = serde_json::to_string(event).ok()?;
    let mut mac = HmacSha256::new_from_slice(client_secret.as_bytes()).ok()?;
    mac.update(canonical.as_bytes());
    let signature = mac.finalize().into_bytes();
    Some(base64::engine::general_purpose::STANDARD.encode(signature))
}

pub(crate) fn send_event(kind: &str, id: &str, value: Option<String>) {
    let Some((session_token, client_secret, nonce)) = state::next_event_context() else {
        return;
    };

    let event = EventBody {
        kind,
        id,
        value,
        nonce: Some(nonce),
    };

    let Some(mac) = sign_event(&event, &client_secret) else {
        return;
    };

    let payload = json!({
        "protocol": 1,
        "type": "event",
        "session": {"token": session_token},
        "event": event,
        "mac": mac
    });

    if let Ok(raw) = serde_json::to_string(&payload) {
        ws_send(&raw);
    }
}
