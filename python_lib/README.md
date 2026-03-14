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

## Installation avec Poetry

```bash
cd python_lib
poetry install
```

Installation depuis PyPI (quand publie):

```bash
pip install pywasm-ui
```

## Publication PyPI avec Poetry

Build local:

```bash
cd python_lib
poetry build
```

Publier sur TestPyPI:

```bash
cd python_lib
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi <TOKEN_TESTPYPI>
poetry publish --repository testpypi
```

Publier sur PyPI:

```bash
cd python_lib
poetry config pypi-token.pypi <TOKEN_PYPI>
poetry publish
```

## Utilisation FastAPI

```python
from fastapi import FastAPI
from pathlib import Path
from pywasm_ui import EventPayload, PyWasmSession, Widget, bootstrap_fastapi_app

app = FastAPI()

def on_click(session: PyWasmSession, event: EventPayload):
	count = int(session.data.get("count", 0)) + 1
	session.data["count"] = count
	return {"id": "label1", "text": f"Clicks: {count}"}

def configure(session: PyWasmSession):
	session.register_event_handler("click", "btn1", on_click)

bootstrap_fastapi_app(
	app,
	Path("web"),
	ws_path="/ws",
	server_secret="change-me",
	initial_widgets=[
		Widget(id="label1", kind="Label", parent="root", props={"text": "Ready"}),
		Widget(id="btn1", kind="Button", parent="root", props={"text": "Click"}),
	],
	configure_session=configure,
	pages={"/": "index.html"},
	health_payload={"status": "ok"},
)
```

## Utilisation Flask

```python
from flask import Flask
from flask_sock import Sock
from pathlib import Path
from pywasm_ui import bootstrap_flask_app

app = Flask(__name__)
sock = Sock(app)
bootstrap_flask_app(
	app,
	sock,
	Path("web"),
	ws_path="/ws",
	server_secret="change-me",
	pages={"/": "index.html"},
	health_payload={"status": "ok", "framework": "flask"},
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
