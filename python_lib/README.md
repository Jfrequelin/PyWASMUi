# pywasm-ui

Bibliotheque Python pour piloter un client UI WASM en mode server-driven.

## Fonctions cle

- protocole JSON valide via Pydantic,
- securite `session_token + HMAC + nonce monotone`,
- fiabilite transport avec `ack` (event traite) et `receipt` (commande serveur recue),
- gestion d'une session UI,
- adaptateurs de transport pour FastAPI et Flask,
- assets frontend (JS + WASM) embarques dans la lib Python,
- objet de communication WASM decoupe en :
	- envoi de commandes (`WasmCommandSender`),
	- reception asynchrone d'evenements (`WasmAsyncEventReceiver`).

## Objets principaux

- `WasmAppCommunication` : orchestration transport `send_commands(...)` + `receive_events()`.
- `WasmWidget` : classe mere de tous les widgets.
- widgets derives :
	- layout/content: `WindowWidget`, `ContainerWidget`, `CardWidget`, `StackWidget`, `RowWidget`, `ListViewWidget`, `HeadingWidget`, `ParagraphWidget`, `DividerWidget`, `LabelWidget`
	- interaction/form: `ButtonWidget`, `IconButtonWidget`, `TextInputWidget`, `TextAreaWidget`, `SliderWidget`, `SelectWidget`, `OptionWidget`, `CheckboxWidget`, `DatePickerWidget`
	- feedback/state: `BadgeWidget`, `AlertWidget`, `ProgressWidget`, `ModalWidget`, `ConnectionStatusWidget`

## Installation locale

```bash
pip install -e ./python_lib
```

## Utilisation FastAPI

```python
from fastapi import FastAPI
from pywasm_ui import EventPayload, PyWasmSession, Widget, mount_fastapi_websocket

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
		Widget(id="label1", kind="Label", parent="root", props={"text": "Ready"}),
		Widget(id="btn1", kind="Button", parent="root", props={"text": "Click"}),
	],
	configure_session=configure,
)

# assets pyWasm servis depuis la lib
from pathlib import Path
from pywasm_ui import mount_fastapi_frontend, mount_fastapi_packaged_assets

mount_fastapi_packaged_assets(app, route_prefix="/pywasm-assets")
mount_fastapi_frontend(
	app,
	Path("web"),
	pages={"/": "index.html"},
	reserved_paths=("ws", "health", "pywasm-assets"),
)
```

## Utilisation Flask

```python
from flask import Flask
from flask_sock import Sock
from pathlib import Path
from pywasm_ui import register_flask_frontend, register_flask_packaged_assets, register_flask_socket

app = Flask(__name__)
sock = Sock(app)
register_flask_socket(sock, path="/ws", server_secret="change-me")
register_flask_packaged_assets(app, route_prefix="/pywasm-assets")
register_flask_frontend(
	app,
	Path("web"),
	pages={"/": "index.html"},
	reserved_paths=("ws", "health", "pywasm-assets"),
)
```

## API callbacks

- `session.register_event_handler(event_kind, widget_id, handler)` : associe un callback a un evenement/widget.
- `session.set_default_event_handler(handler)` : fallback si aucun handler specifique.
- `handler(session, event)` peut renvoyer :
	- `dict` avec `id` + champs de patch (`{"id": "label1", "text": "..."}`),
	- `OutgoingMessage`,
	- `str` JSON deja serialize,
	- ou une liste de ces elements.
