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

Alternative avec Poetry (pour packager/publier la lib):

```bash
cd python_lib
poetry install
cd ..
```

## Quick Start Apres Clone

```bash
git clone https://github.com/Jfrequelin/PyWASMui.git
cd PyWASMui

python -m pip install -r server/requirements.txt
python -m pip install -e python_lib
python -m pip install -r requirements-test.txt

# premier demarrage direct: client/wasm_ui/pkg est partage dans le repo
python -m uvicorn server.app.examples.fastapi.fastapi_server:app --host 127.0.0.1 --port 8000
```

Dans un second terminal:

```bash
curl -sS http://127.0.0.1:8000/health
python -m pytest tests/unit/test_widgets.py tests/integration/test_fastapi_websocket.py
```

## Outils Rust/WASM (une seule fois)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
. "$HOME/.cargo/env"
rustup target add wasm32-unknown-unknown
cargo install wasm-pack
```

## Lancement local

Le package WASM precompile (`client/wasm_ui/pkg`) est commit dans le depot,
donc le premier lancement fonctionne sans build Rust local.

Terminal 1 (rebuild WASM optionnel, seulement apres modification du runtime Rust):

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

Vous pouvez eviter de recoder les routes frontend (`/`, assets, fallback SPA),
le websocket et la route health avec un seul helper :

```python
from pathlib import Path
from pywasm_ui import bootstrap_fastapi_app

bootstrap_fastapi_app(
	app,
	Path("web"),
	ws_path="/ws",
	server_secret="change-me",
	initial_widgets=[...],
	pages={
		"/": "index.html",
		"/dashboard": "pages/dashboard.html",
		"/settings": "pages/settings.html",
	},
	assets_route_prefix="/pywasm-assets",
	health_path="/health",
	health_payload={"status": "ok"},
)
```

Si vous voulez garder le controle fin, vous pouvez appeler les helpers separement :

```python
from pathlib import Path
from pywasm_ui import mount_fastapi_frontend, mount_fastapi_packaged_assets

mount_fastapi_packaged_assets(app, route_prefix="/pywasm-assets")

mount_fastapi_frontend(
	app,
	Path("web"),
	pages={
		"/": "index.html",
		"/dashboard": "pages/dashboard.html",
		"/settings": "pages/settings.html",
	},
	reserved_paths=("ws", "health", "pywasm-assets"),
)
```

## Integration Jinja2 (sans changer vos pages)

Pour conserver vos templates Jinja2 et vos libs habituelles, vous pouvez juste
injecter un bloc PyWASMui dans la page:

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

Necessaire uniquement si vous modifiez `client/wasm_ui/src`.

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```

## Publication PyPI avec Poetry

```bash
# depuis la racine
make poetry-build

cd python_lib
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi <TOKEN_TESTPYPI>
poetry publish --repository testpypi

poetry config pypi-token.pypi <TOKEN_PYPI>
poetry publish
```
