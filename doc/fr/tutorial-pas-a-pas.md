# Tutoriel Complet Pas A Pas (PyWASMui)

Ce guide est un parcours complet pour partir de zero et arriver a une application PyWASMui operationnelle, testee, et prete a etre packagee.

Le tutoriel est ecrit pour Linux/macOS, mais la logique est identique sous Windows (PowerShell).

## 1. Objectif Du Tutoriel

A la fin de ce tutoriel, vous saurez:

- installer le projet localement
- lancer les exemples FastAPI
- creer un mini ecran avec widgets
- gerer des interactions client -> serveur
- appliquer des styles et des tooltips
- utiliser le protocole websocket de base
- executer les tests
- builder le runtime WASM
- generer un wheel Python

## 2. Prerequis

- Python 3.11+
- pip
- Rust stable (si vous voulez rebuild le WASM)
- wasm-pack (si vous voulez rebuild le WASM)
- git

## 3. Recuperer Le Projet

```bash
git clone https://github.com/Jfrequelin/PyWASMui.git
cd PyWASMui
```

## 4. Installer Les Dependances

### 4.1 Dependances Serveur Et Bibliotheque

```bash
python -m pip install -r server/requirements.txt
python -m pip install -e python_lib
```

### 4.2 Dependances De Test

```bash
python -m pip install -r requirements-test.txt
```

### 4.3 Option Poetry (packaging)

```bash
cd python_lib
poetry install
cd ..
```

## 5. Premier Lancement (Sans Rebuild WASM)

Le depot contient deja un package WASM precompile (`client/wasm_ui/pkg`), donc vous pouvez lancer directement.

```bash
python -m uvicorn server.app.examples.fastapi.fastapi_server:app --host 127.0.0.1 --port 8000
```

Puis ouvrir:

- `http://127.0.0.1:8000`

Verification health:

```bash
curl -sS http://127.0.0.1:8000/health
```

## 6. Lancer Les Exemples FastAPI

Les exemples servent de guide progressif.

### 6.1 Exemple 01

```bash
python -m uvicorn server.app.examples.fastapi.01_single_widget_fastapi:app --host 127.0.0.1 --port 8000
```

### 6.2 Exemple 10 (catalogue complet)

```bash
python -m uvicorn server.app.examples.fastapi.10_widgets_catalog_fastapi:app --host 127.0.0.1 --port 8000
```

### 6.3 Un Exemple Par Widget

```bash
python -m uvicorn server.app.examples.fastapi.widgets.button_widget_fastapi:app --host 127.0.0.1 --port 8000
python -m uvicorn server.app.examples.fastapi.widgets.select_widget_fastapi:app --host 127.0.0.1 --port 8001
```

Liste complete: `server/app/examples/fastapi/EXAMPLES.md`.

## 7. Ecrire Votre Premier Ecran

Creez un fichier `my_app.py`:

```python
from fastapi import FastAPI
from pathlib import Path

from pywasm_ui import (
    ButtonWidget,
    LabelWidget,
    PyWasmSession,
    bootstrap_fastapi_app,
)


def on_click(session: PyWasmSession):
    count = int(session.data.get("count", 0)) + 1
    session.data["count"] = count
    return [session.update("label_count", text=f"Compteur: {count}")]


app = FastAPI(title="Demo PyWASMui")

widgets = [
    LabelWidget(id="label_count", parent="root", text="Compteur: 0"),
    ButtonWidget(id="btn_inc", parent="root", text="Incrementer", on_click=on_click),
]

bootstrap_fastapi_app(
    app,
    Path("server/app/examples/web"),
    ws_path="/ws",
    server_secret="change-me",
    initial_widgets=widgets,
)
```

Lancer:

```bash
python -m uvicorn my_app:app --host 127.0.0.1 --port 8000
```

## 8. Comprendre Le Flux Interaction

Quand l utilisateur clique:

1. le client envoie un event websocket
2. la session Python traite l event
3. votre callback retourne des reponses (`session.update`, `session.create`, `session.delete`)
4. le client applique les patchs

Ce modele vous permet de garder la logique metier cote Python.

## 9. Ajouter Des Tooltips Et Du Style

Exemple sur un bouton:

```python
from pywasm_ui import ButtonWidget, Style

btn = ButtonWidget(
    id="btn_help",
    text="Survolez moi",
    style=Style(background_color="#0f766e", color="#ffffff"),
)
btn.tooltip("Astuce: ceci est une info-bulle", delay_ms=800)
```

Note:

- les info-bulles sont configurees pour rester au-dessus des autres widgets (z-index eleve)
- le delay est configurable par widget

## 10. Logging (debug, info, warning, error)

Le projet supporte un niveau de log configurable via variable d environnement:

```bash
export PYWASM_LOG_LEVEL=DEBUG
python -m uvicorn server.app.examples.fastapi.10_widgets_catalog_fastapi:app --host 127.0.0.1 --port 8000
```

Niveaux acceptes:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

Les logs incluent notamment:

- ouverture/fermeture websocket
- sessions creees/reutilisees
- origines websocket refusees
- violations protocole

## 11. Rebuild WASM (si vous modifiez Rust)

Installer outils (une fois):

```bash
rustup target add wasm32-unknown-unknown
cargo install wasm-pack
```

Build:

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```

Sync vers les assets Python:

```bash
rsync -a --delete pkg/ ../../python_lib/pywasm_ui/frontend/wasm_ui/pkg/
```

## 12. Tests Recommandes

### 12.1 Unitaires Rapides

```bash
python -m pytest tests/unit/test_widgets.py tests/unit/test_adapters.py -q
```

### 12.2 Websocket Integration

```bash
python -m pytest tests/integration/test_fastapi_websocket.py -q
```

### 12.3 Suite Complete

```bash
python -m pytest
```

## 13. Generer Un Wheel Python

Le packaging Python est dans `python_lib/`.

```bash
cd python_lib
python -m build --wheel
ls -lh dist/*.whl
```

Exemple de sortie:

- `dist/pywasm_ui-0.1.0-py3-none-any.whl`

## 14. Structure Importante Du Depot

- `python_lib/pywasm_ui/` : coeur de la bibliotheque Python
- `client/wasm_ui/` : runtime Rust -> WASM
- `server/app/examples/` : applications d exemples
- `server/app/examples/web/` : frontend statique et themes
- `tests/` : unit + integration
- `doc/` : documentation FR/EN

## 15. Probleme Courants Et Solutions

- Port deja utilise:

```bash
fuser -k 8000/tcp || true
```

- L interface ne reflete pas vos changements Rust:

1. rebuild `client/wasm_ui/pkg`
2. resynchroniser vers `python_lib/pywasm_ui/frontend/wasm_ui/pkg`
3. relancer le serveur
4. hard refresh navigateur

- Erreur websocket immediate:

- verifier que l URL client pointe bien vers `/ws`
- verifier les logs backend (`PYWASM_LOG_LEVEL=DEBUG`)
- verifier l origine websocket si `PYWASM_ALLOWED_WS_ORIGINS` est definie

## 16. Et Ensuite

Vous pouvez maintenant:

1. partir de `server/app/examples/fastapi/10_widgets_catalog_fastapi.py`
2. extraire vos propres composants metier
3. ajouter une couche auth (OIDC/OAuth/Firebase) cote serveur
4. industrialiser CI (tests + build wheel + publication)

Pour aller plus loin:

- `doc/fr/python-api.md`
- `doc/fr/widgets-and-styling.md`
- `doc/fr/websocket-protocol.md`
- `doc/fr/testing-and-dev.md`
