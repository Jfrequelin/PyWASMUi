# Python API (`pywasm_ui`)

## Main Entry Points

- `mount_fastapi_websocket(app, ...)`
- `mount_fastapi_frontend(app, ...)`
- `mount_fastapi_socket(app, ...)` (compatibility alias)
- `register_flask_socket(sock, ...)`
- `register_flask_frontend(app, ...)`
- adapters: `pywasm_ui.fastapi`, `pywasm_ui.flask`
- `PyWasmSession`
- standard widgets (full list below)
- styling: `Style`
- patch helpers: `set_text`, `patch_value`, `patch_enabled`, `patch_classes`, `patch_attrs`, `patch_remove_attrs`, `patch_style`, `merge_patches`
- snippets/runtime: `render_embed_snippet`, `write_js_runtime_config`

## Full Standard Widget Catalog

- `WindowWidget`
- `ContainerWidget`
- `CardWidget`
- `StackWidget`
- `RowWidget`
- `ListViewWidget`
- `HeadingWidget`
- `ParagraphWidget`
- `LabelWidget`
- `DividerWidget`
- `BadgeWidget`
- `AlertWidget`
- `ButtonWidget`
- `IconButtonWidget`
- `TextInputWidget`
- `TextAreaWidget`
- `SliderWidget`
- `SelectWidget`
- `OptionWidget`
- `CheckboxWidget`
- `DatePickerWidget`
- `ProgressWidget`
- `ModalWidget`
- `ConnectionStatusWidget`

## FastAPI Integration

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

## Session API

- `session.register_event_handler(event_kind, widget_id, handler)`
- `session.set_default_event_handler(handler)`
- `session.data` for per-session business state

Handlers can return:

- patch dict (`{"id": ..., ...}`)
- `OutgoingMessage`
- JSON string
- list of these types

## Styling API

### Style at creation time

```python
from pywasm_ui import LabelWidget, Style

label = LabelWidget(id="label1", text="Hello", style=Style(font_size="18px", color="#111"))
```

### Style after creation

```python
button.style.set(background_color="#0ea5e9", border="none")
button.style.remove("border")
button.style.clear()
```

### Style patch helper

```python
from pywasm_ui import patch_style

patch = patch_style("label1", {"font_size": "20px", "opacity": 0.8})
```

## Packaged frontend assets and custom pages

Recommended distribution pattern:

- serve pyWasm runtime assets from the Python package (`/pywasm-assets`),
- keep your own `index.html` and pages in your app repository.

```python
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

In your user-owned `index.html`, load the packaged runtime:

```html
<script type="module" src="/pywasm-assets/src/main.js"></script>
```

## JS runtime config (websocket host/port)

The client can still read `pywasm.runtime.json` when exposed by your app.
You can manage this file from the Python library:

```python
from pywasm_ui import write_js_runtime_config

write_js_runtime_config(
    "client/config/pywasm.runtime.json",
    ws_host="192.168.1.20",
    ws_port=9000,
    ws_path="/ws",
    ws_protocol="ws",  # or "wss"
)
```

If `ws_host` or `ws_port` is `None`, the client falls back to the current page host/port.

## Flask Integration

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
