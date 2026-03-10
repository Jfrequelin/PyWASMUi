# PyWASMui

Framework UI server-driven avec serveur Python (FastAPI), moteur UI Rust/WASM, et bridge JavaScript minimal via WebSocket.

Le frontend suit un pattern hybride:
- assets runtime PyWASMui (JS + WASM) servis depuis la lib Python (`/pywasm-assets`),
- pages HTML utilisateur (comme `index.html`) servies depuis votre projet.

Commandes rapides:

```bash
make run-fastapi-single
make run-flask-single
```

## Documentation

- Index bilingue: `doc/README.md`
- Version FR: `doc/fr/README.md`
- Version EN: `doc/en/README.md`

## Structure

- `server/` : serveur FastAPI + protocole + securite HMAC/nonce
- `client/` : app web statique + bridge WebSocket JS minimal
- `client/wasm_ui/` : moteur UI Rust compile en WASM
- `python_lib/` : bibliotheque Python reutilisable (`pywasm_ui`) pour FastAPI/Flask

## Prerequis

- Python 3.11+
- Rust stable + target `wasm32-unknown-unknown`
- `wasm-pack`

## Installation rapide

```bash
# depuis la racine
python -m pip install -r server/requirements.txt

# installer la bibliotheque locale reutilisable
python -m pip install -e python_lib

# une seule fois (outillage Rust/WASM)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
. "$HOME/.cargo/env"
rustup target add wasm32-unknown-unknown
cargo install wasm-pack
```

Dependances de test:

```bash
python -m pip install -r requirements-test.txt
```

## Quick Start Apres Clone

```bash
git clone https://github.com/Jfrequelin/PyWASMui.git
cd PyWASMui

# runtime + lib locale
python -m pip install -r server/requirements.txt
python -m pip install -e python_lib

# dependances de test
python -m pip install -r requirements-test.txt

# demarrage immediat (WASM deja precompile dans le repo)
python -m uvicorn server.app.examples.fastapi.fastapi_server:app --host 127.0.0.1 --port 8000
```

Dans un autre terminal:

```bash
curl -sS http://127.0.0.1:8000/health
python -m pytest tests/unit/test_widgets.py tests/integration/test_fastapi_websocket.py
```

## Reutilisation en bibliotheque (FastAPI / Flask)

FastAPI :
```python
from fastapi import FastAPI
from pathlib import Path

from pywasm_ui import (
	mount_fastapi_frontend,
	mount_fastapi_packaged_assets,
	mount_fastapi_websocket,
	ButtonWidget,
	EventPayload,
	LabelWidget,
	PyWasmSession,
)

app = FastAPI()

def on_click(session: PyWasmSession, event: EventPayload):
	count = int(session.data.get("count", 0)) + 1
	session.data["count"] = count
	return {"id": "label1", "text": f"Clicks: {count}"}

def configure(session: PyWasmSession):
	session.register_event_handler("click", "btn1", on_click)

mount_fastapi_websocket(
	app,
	path="/ws",
	server_secret="change-me",
	initial_widgets=[
		LabelWidget(id="label1", parent="root", text="Ready"),
		ButtonWidget(id="btn1", parent="root", text="Click"),
	],
	configure_session=configure,
)

mount_fastapi_packaged_assets(app, route_prefix="/pywasm-assets")

mount_fastapi_frontend(
	app,
	Path("web"),
	pages={
		"/": "index.html",
		"/dashboard": "pages/dashboard.html",
		"/admin": "pages/admin.html",
	},
	reserved_paths=("ws", "health", "pywasm-assets"),
)
```

Flask :
```python
from pathlib import Path

from flask import Flask
from flask_sock import Sock
from pywasm_ui import register_flask_frontend, register_flask_packaged_assets, register_flask_socket

app = Flask(__name__)
sock = Sock(app)
register_flask_socket(sock, path="/ws", server_secret="change-me")
register_flask_packaged_assets(app, route_prefix="/pywasm-assets")
register_flask_frontend(
	app,
	Path("web"),
	pages={"/admin": "pages/admin.html"},
	reserved_paths=("ws", "health", "pywasm-assets"),
)
```

Communication interne WASM cote serveur :
- envoi : `WasmCommandSender`
- reception asynchrone : `WasmAsyncEventReceiver`
- orchestration : `WasmAppCommunication`

## Integration naturelle avec Jinja2

Si vous voulez garder vos templates/pages existants (Jinja2, HTMX, etc.),
vous pouvez simplement injecter le widget runtime dans un `div` sans deleguer
tout le routage frontend a PyWASMui.

FastAPI + Jinja2 :

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pywasm_ui import mount_fastapi_websocket, render_embed_snippet

app = FastAPI()
templates = Jinja2Templates(directory="templates")

mount_fastapi_websocket(app, path="/widgets/ws", server_secret="change-me", initial_widgets=[...])

@app.get("/dashboard")
def dashboard(request: Request):
	pywasm_embed = render_embed_snippet(
		ws_path="/widgets/ws",
		mount_element_id="widgets-area",
	)
	return templates.TemplateResponse(
		"dashboard.html",
		{
			"request": request,
			"pywasm_embed": pywasm_embed,
		},
	)
```

Template `dashboard.html` :

```html
<section>
  <h2>Mon dashboard metier</h2>
  {{ pywasm_embed|safe }}
</section>
```

## Lancement developpement

Le package WASM precompile (`client/wasm_ui/pkg`) est versionne dans le depot,
donc le projet fonctionne des le premier clone sans build Rust local.

```bash
python -m uvicorn server.app.examples.fastapi.fastapi_server:app --reload --host 127.0.0.1 --port 8000
```

Ouvrir `http://127.0.0.1:8000`.

## Serie d'exemples progressifs (FastAPI)

Voir `server/app/examples/fastapi/EXAMPLES.md` pour la liste complete.

Lancer directement un exemple :

```bash
python -m uvicorn server.app.examples.fastapi.01_single_widget_fastapi:app --host 127.0.0.1 --port 8000
```

## Build WASM

Rebuild utile uniquement si vous modifiez `client/wasm_ui/src`.

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```

## Flux MVP

1. Le serveur envoie `init` puis `create` (label + bouton).
2. WASM cree le DOM.
3. Click sur le bouton -> evenement signe avec HMAC + nonce.
4. Serveur verifie et renvoie un patch `update` du label.
