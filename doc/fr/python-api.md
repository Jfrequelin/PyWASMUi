# API Python (`pywasm_ui`)

## Points d'entree

- `bootstrap_fastapi_app(app, client_root, ...)`
- `bootstrap_flask_app(app, sock, client_root, ...)`
- adaptateurs: `pywasm_ui.fastapi.bootstrap_app(...)`, `pywasm_ui.flask.bootstrap_app(...)`
- `mount_fastapi_websocket(app, ...)`
- `mount_fastapi_frontend(app, ...)`
- `mount_fastapi_socket(app, ...)` (alias de compatibilite)
- `register_flask_socket(sock, ...)`
- `register_flask_frontend(app, ...)`
- adaptateurs: `pywasm_ui.fastapi`, `pywasm_ui.flask`
- `PyWasmSession`
- widgets HTML (voir liste complete ci-dessous)
- style: `Style`
- helpers patch: `set_text`, `patch_value`, `patch_enabled`, `patch_classes`, `patch_attrs`, `patch_remove_attrs`, `patch_style`, `merge_patches`
- snippets/runtime: `render_embed_snippet`, `write_js_runtime_config`
- events types: `to_typed_event`, `ClickEvent`, `TextInputChangeEvent`, `SliderChangeEvent`
- theme: `ThemeTokens`, `apply_theme`
- routing leger: `page`, `register_fastapi_pages`, `register_flask_pages`

## Catalogue complet des widgets HTML

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

## Integration FastAPI

```python
from fastapi import FastAPI
from pathlib import Path
from pywasm_ui import (
    ButtonWidget,
    EventPayload,
    LabelWidget,
    PyWasmSession,
    bootstrap_fastapi_app,
)

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
        LabelWidget(id="label1", parent="root", text="Ready"),
        ButtonWidget(id="btn1", parent="root", text="Click me"),
    ],
    configure_session=configure,
    pages={"/": "index.html"},
    health_payload={"status": "ok"},
)
```

## API Session

- `session.register_event_handler(event_kind, widget_id, handler)`
- `session.set_default_event_handler(handler)`
- `session.data` pour stocker l'etat metier de la session

Helpers d'events types:

- `session.on_click_typed(widget_or_id, handler)`
- `session.on_change_typed(widget_or_id, handler)`

```python
from pywasm_ui import ClickEvent, TextInputChangeEvent

def on_click(session: PyWasmSession, event: ClickEvent):
    return {"id": "status", "text": f"clicked: {event.widget_id}"}

def on_change(session: PyWasmSession, event: TextInputChangeEvent):
    return {"id": "preview", "text": event.text}

session.on_click_typed("btn1", on_click)
session.on_change_typed("input1", on_change)
```

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

## Tokens de theme

`apply_theme` permet de definir des styles par defaut (kind/class) au niveau session.

```python
from pywasm_ui import ThemeTokens, apply_theme

apply_theme(session)  # theme par defaut

apply_theme(
    session,
    ThemeTokens(
        primary_color="#ff006e",
        primary_contrast_color="#ffffff",
        border_radius="10px",
    ),
)
```

## Assets frontend packages et pages custom

Pattern recommande pour distribuer la lib:

- servir les assets runtime PyWASMui depuis la lib Python (`/pywasm-assets`),
- conserver `index.html` et les pages dans le repo de l'application.

```python
from pathlib import Path
from pywasm_ui import bootstrap_fastapi_app

bootstrap_fastapi_app(
    app,
    Path("web"),
    ws_path="/ws",
    server_secret="change-me",
    pages={"/": "index.html"},
    assets_route_prefix="/pywasm-assets",
    health_path="/health",
)
```

Dans ton `index.html` (projet utilisateur), charge le runtime package:

```html
<script type="module" src="/pywasm-assets/src/main.js"></script>
```

## Configuration runtime JS (IP/port websocket)

Le client peut toujours lire `pywasm.runtime.json` si ton app expose ce fichier.
Tu peux le gerer depuis la bibliotheque Python:

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

Tu peux aussi passer des variables runtime partagees (serialisables en JSON) vers le JavaScript navigateur,
utile pour des donnees de graphiques ou des schemas dynamiques:

```python
from pywasm_ui import write_js_runtime_config

write_js_runtime_config(
        "client/config/pywasm.runtime.json",
        shared={
                "chart": {
                        "labels": ["Jan", "Fev", "Mar"],
                        "values": [12, 18, 15],
                },
                "schema": {
                        "kind": "flow",
                        "nodes": [{"id": "A"}, {"id": "B"}],
                },
        },
)
```

Au runtime, le frontend expose:

- `window.__PYWASM_SHARED_VARS__`: objet courant des variables partagees.
- `window.pywasmShared`: API helper (`get`, `set`, `merge`, `all`, `subscribe`).
- Evenement `window` `pywasm:shared-update`: emis apres `set`/`merge`.

Exemple en JS custom:

```js
const chart = window.pywasmShared.get('chart', { labels: [], values: [] });

const unsubscribe = window.pywasmShared.subscribe(({ state }) => {
    const nextChart = state.chart;
    if (nextChart) {
        renderChart(nextChart);
    }
});

window.addEventListener('pywasm:shared-update', (event) => {
    console.log('Variables partagees mises a jour:', event.detail);
});
```

## Integration Flask

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

## Routing Python leger (multipage + guard)

```python
from pathlib import Path
from fastapi import FastAPI
from pywasm_ui import page, register_fastapi_pages

app = FastAPI()

register_fastapi_pages(
    app,
    Path("web"),
    [
        page("/", "index.html"),
        page("/admin", "admin.html", guard=lambda request: request.headers.get("x-admin") == "1"),
    ],
)
```
