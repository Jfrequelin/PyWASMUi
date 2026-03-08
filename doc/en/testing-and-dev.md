# Testing and Development

## Run all tests

```bash
cd /home/rlv/Work/projects/pyWasm
/home/rlv/.pyenv/versions/3.11.14/bin/python -m pytest
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
cd /home/rlv/Work/projects/pyWasm/client/wasm_ui
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
