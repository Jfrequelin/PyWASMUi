# Architecture

## High-Level View

`PyWASMui` uses a **server-driven UI** model:

- The Python server drives UI structure and updates.
- The Rust/WASM runtime renders DOM and applies patches.
- JavaScript is a minimal transport bridge (WebSocket only).

## Components

### Python Server

- Location: `server/` and `python_lib/pywasm_ui/`
- Responsibilities:
  - manage UI sessions (`PyWasmSession`)
  - define widgets
  - receive client events
  - run business callbacks
  - emit commands (`create`, `update`, `delete`)

### JavaScript Bridge

- Location: `client/src/main.js`
- Responsibilities:
  - open WebSocket connection
  - forward server messages to WASM
  - forward WASM messages through `wsSend`
  - track pending interactive widget commands
  - handle `ack` (client -> server) and `receipt` (server -> client)
  - handle connection status display

### Rust/WASM Runtime

- Location: `client/wasm_ui/src/`
- Responsibilities:
  - parse JSON messages
  - render widgets to DOM
  - apply patches (`text`, `value`, `enabled`, `classes`, `attrs`, `style`)
  - capture user events and send `event` messages

## Runtime Flow

1. Connect to `/ws`.
2. Receive `init` then initial `create` commands.
3. Render DOM in browser.
4. User interaction -> `event` message.
5. Server processing -> `update/create/delete` response.
6. Client sends `receipt` to confirm delivery of server commands.

## Transport Reliability

- client -> server: event carries `nonce`, then server returns `ack` when processed
- server -> client: commands are tagged with `meta.command_id`
- client -> server: `receipt` confirms command delivery

## Session Resume on Refresh

- Client stores `session_token` in `localStorage`.
- After refresh, reconnect uses `/ws?session_token=...`.
- Server can reattach the existing session and replay UI state.

## Security Note

Wrapper mode accepts unsigned events. When `mac` is present, MAC + monotonic nonce checks are enforced.
