use wasm_bindgen::prelude::*;
mod dom;
mod events;
mod handlers;
mod models;
mod state;
mod transport;

#[wasm_bindgen]
pub fn wasm_set_incoming_message_handler(_handler: js_sys::Function) {}

#[wasm_bindgen]
pub fn wasm_on_websocket_open() {
    wasm_set_connection_status("connected");
    web_sys::console::log_1(&JsValue::from_str("WebSocket connected"));
}

#[wasm_bindgen]
pub fn wasm_set_connection_status(status: &str) {
    dom::update_connection_status_badge(status);
}

#[wasm_bindgen]
pub fn wasm_boot() {
    console_error_panic_hook::set_once();
    dom::ensure_root_widget();
}

#[wasm_bindgen]
pub fn wasm_handle_server_message(message: &str) {
    handlers::handle_server_message(message);
}
