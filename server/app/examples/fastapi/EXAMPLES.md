# FastAPI Example Series

Progressive examples that showcase server-driven UI patterns with PyWASMui.

Common setup used by these examples:

- Websocket endpoint at `/ws`
- Runtime assets at `/pywasm-assets`
- Frontend page from `server/app/examples/web/index.html`
- Health probe at `/health`

## 01. Single Widget

File: `server/app/examples/fastapi/01_single_widget_fastapi.py`

```bash
python -m uvicorn server.app.examples.fastapi.01_single_widget_fastapi:app --host 127.0.0.1 --port 8000
```

## 02. Widget Composition

File: `server/app/examples/fastapi/02_widget_composition_fastapi.py`

```bash
python -m uvicorn server.app.examples.fastapi.02_widget_composition_fastapi:app --host 127.0.0.1 --port 8000
```

## 03. Runtime Style Updates

File: `server/app/examples/fastapi/03_style_updates_fastapi.py`

```bash
python -m uvicorn server.app.examples.fastapi.03_style_updates_fastapi:app --host 127.0.0.1 --port 8000
```

## 04. Form Controls

File: `server/app/examples/fastapi/05_form_controls_fastapi.py`

```bash
python -m uvicorn server.app.examples.fastapi.05_form_controls_fastapi:app --host 127.0.0.1 --port 8000
```

## 05. All Widgets Showcase

File: `server/app/examples/fastapi/all_widgets_fastapi.py`

```bash
python -m uvicorn server.app.examples.fastapi.all_widgets_fastapi:app --host 127.0.0.1 --port 8000
```

## 10. Widgets Catalog

File: `server/app/examples/fastapi/10_widgets_catalog_fastapi.py`

```bash
python -m uvicorn server.app.examples.fastapi.10_widgets_catalog_fastapi:app --host 127.0.0.1 --port 8000
```
