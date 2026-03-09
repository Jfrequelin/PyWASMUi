# Demarrage Rapide

## Prerequis

- Python 3.11+
- Rust stable
- target Rust `wasm32-unknown-unknown`
- `wasm-pack`

## Installation

Depuis la racine du projet:

```bash
python -m pip install -r server/requirements.txt
python -m pip install -e python_lib
```

## Outils Rust/WASM (une seule fois)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
. "$HOME/.cargo/env"
rustup target add wasm32-unknown-unknown
cargo install wasm-pack
```

## Lancement local

Terminal 1 (build WASM):

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```

Terminal 2 (serveur FastAPI):

```bash
python -m uvicorn server.app.examples.fastapi.fastapi_server:app --host 127.0.0.1 --port 8000
```

Ensuite ouvrir `http://127.0.0.1:8000`.

## Verifications rapides

```bash
curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:8000 | head -n 5
```

## Integration simplifiee (pages multiples)

Vous pouvez eviter de recoder les routes frontend (`/`, assets, fallback SPA)
en utilisant le helper de la lib :

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

## Integration Jinja2 (sans changer vos pages)

Pour conserver vos templates Jinja2 et vos libs habituelles, vous pouvez juste
injecter un bloc pyWasm dans la page:

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

Dans le template:

```html
{{ pywasm_embed|safe }}
```

## Build production

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```
