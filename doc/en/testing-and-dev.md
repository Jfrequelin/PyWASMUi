# Testing and Development

## Quick Test Path After Clone

```bash
python -m pip install -r requirements-test.txt

# fast smoke path
python -m pytest tests/unit/test_widgets.py tests/integration/test_fastapi_websocket.py

# full suite
python -m pytest
```

Optional Selenium catalog (Chrome required):

```bash
python -m pytest tests/integration/test_selenium_widgets_catalog.py -q
```

## Run all tests

```bash
python -m pytest
```

## Coverage Areas

- unit tests: `tests/unit/`
- integration tests: `tests/integration/`

The suite covers:

- session lifecycle (`init`, reconnect, replay)
- WebSocket protocol flow
- widget payloads
- patch helpers (including `patch_style`)

## Build WASM

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```

## Recommended Dev Loop

1. Update Python or Rust code.
2. Run `pytest`.
3. Rebuild WASM if Rust runtime changed.
4. Restart FastAPI if needed.
5. Validate behavior in browser.

## Port Troubleshooting

```bash
fuser -k 8000/tcp || true
fuser -k 5173/tcp || true
```

Server health check:

```bash
curl -sS http://127.0.0.1:8000/health
```
