use wasm_bindgen::prelude::*;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = globalThis, js_name = wsSend)]
    pub(crate) fn ws_send(message: &str);
}
