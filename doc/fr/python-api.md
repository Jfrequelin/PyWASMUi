# API Python (`pywasm_ui`)

## Points d'entree

- `mount_fastapi_websocket(app, ...)`
- `register_flask_socket(sock, ...)`
- `PyWasmSession`
- widgets: `LabelWidget`, `ButtonWidget`, `TextInputWidget`, `ContainerWidget`, `WindowWidget`, `ListViewWidget`
- style: `Style`
- helpers patch: `patch_text`, `patch_value`, `patch_enabled`, `patch_classes`, `patch_attrs`, `patch_remove_attrs`, `patch_style`, `merge_patches`

## Integration FastAPI

```python
from fastapi import FastAPI
from pywasm_ui import ButtonWidget, EventPayload, LabelWidget, PyWasmSession, mount_fastapi_websocket

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
        ButtonWidget(id="btn1", parent="root", text="Click me"),
    ],
    configure_session=configure,
)
```

## API Session

- `session.register_event_handler(event_kind, widget_id, handler)`
- `session.set_default_event_handler(handler)`
- `session.data` pour stocker l'etat metier de la session

Les handlers peuvent retourner:

- dict patch (`{"id": ..., ...}`)
- `OutgoingMessage`
- string JSON
- liste de ces types

## API Style

### Style a la creation

```python
from pywasm_ui import LabelWidget, Style

label = LabelWidget(id="label1", text="Hello", style=Style(font_size="18px", color="#111"))
```

### Style apres creation

```python
button.style.set(background_color="#0ea5e9", border="none")
button.style.remove("border")
button.style.clear()
```

### Patch style

```python
from pywasm_ui import patch_style

patch = patch_style("label1", {"font_size": "20px", "opacity": 0.8})
```

## Configuration runtime JS (IP/port websocket)

Le client lit automatiquement `client/config/pywasm.runtime.json`.
Tu peux gerer ce fichier depuis la bibliotheque Python:

```python
from pywasm_ui import write_js_runtime_config

write_js_runtime_config(
    "client/config/pywasm.runtime.json",
    ws_host="192.168.1.20",
    ws_port=9000,
    ws_path="/ws",
    ws_protocol="ws",  # ou "wss"
)
```

Laisser `ws_host` ou `ws_port` a `None` force le client a reutiliser l'hote/port de la page courante.

## Integration Flask

```python
from flask import Flask
from flask_sock import Sock
from pywasm_ui import register_flask_socket

app = Flask(__name__)
sock = Sock(app)
register_flask_socket(sock, path="/ws", server_secret="change-me")
```
