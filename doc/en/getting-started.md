# Getting Started

## Prerequisites

- Python 3.11+
- Rust stable
- Rust target `wasm32-unknown-unknown`
- `wasm-pack`

## Installation

From the project root:

```bash
python -m pip install -r server/requirements.txt
python -m pip install -e python_lib
```

## Rust/WASM Tooling (one-time)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
. "$HOME/.cargo/env"
rustup target add wasm32-unknown-unknown
cargo install wasm-pack
```

## Local Run

The precompiled WASM package (`client/wasm_ui/pkg`) is committed in the
repository, so first run works without a local Rust build.

Terminal 1 (optional WASM rebuild, only after Rust runtime changes):

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```

Terminal 2 (FastAPI server):

```bash
python -m uvicorn server.app.examples.fastapi.fastapi_server:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

## Quick Checks

```bash
curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:8000 | head -n 5
```

## Simplified Integration (multi-page)

To avoid rewriting frontend routes (`/`, assets, SPA fallback), use the
library helper:

```python
from pathlib import Path
from pywasm_ui import mount_fastapi_frontend

mount_fastapi_frontend(
	app,
	Path("client"),
	pages={
		"/": "index.html",
		"/dashboard": "pages/dashboard.html",
		"/settings": "pages/settings.html",
	},
)
```

## Jinja2 Integration (keep your existing pages)

To keep your existing Jinja2 templates and other frontend libraries, inject a
small pyWasm block into your page:

```python
from pywasm_ui import mount_fastapi_websocket, render_embed_snippet

mount_fastapi_websocket(app, path="/widgets/ws", server_secret="change-me", initial_widgets=[...])

@app.get("/dashboard")
def dashboard(request: Request):
	return templates.TemplateResponse(
		"dashboard.html",
		{
			"request": request,
			"pywasm_embed": render_embed_snippet(
				ws_path="/widgets/ws",
				mount_element_id="widgets-area",
			),
		},
	)
```

Inside the template:

```html
{{ pywasm_embed|safe }}
```

## Production Build

Only needed if you changed `client/wasm_ui/src`.

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```
