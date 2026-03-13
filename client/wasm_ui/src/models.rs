use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub(crate) struct Widget {
    pub(crate) id: String,
    pub(crate) kind: String,
    pub(crate) parent: String,
    #[serde(default)]
    pub(crate) props: Value,
    #[serde(default)]
    pub(crate) children: Vec<String>,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub(crate) struct SessionRef {
    pub(crate) token: String,
}

#[derive(Clone, Debug, Default)]
pub(crate) struct ClientState {
    pub(crate) session_token: Option<String>,
    pub(crate) client_secret: Option<String>,
    pub(crate) nonce: u64,
    pub(crate) connection_status: Option<String>,
    pub(crate) widgets: HashMap<String, Widget>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct InitPayload {
    pub(crate) protocol: u8,
    pub(crate) r#type: String,
    pub(crate) session: SessionRef,
    pub(crate) client_secret: String,
}

#[derive(Debug, Deserialize)]
pub(crate) struct IncomingMessage {
    pub(crate) protocol: u8,
    pub(crate) r#type: String,
    pub(crate) widget: Option<Widget>,
    pub(crate) patch: Option<Value>,
}

#[derive(Serialize)]
pub(crate) struct EventBody<'a> {
    pub(crate) kind: &'a str,
    pub(crate) id: &'a str,
    pub(crate) value: Option<String>,
    pub(crate) nonce: Option<u64>,
}
