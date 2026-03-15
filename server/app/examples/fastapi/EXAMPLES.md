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

## 11. One Example Per Widget

Folder: `server/app/examples/fastapi/widgets/`

Each file exposes `app` and demonstrates exactly one widget in isolation.

Example commands:

```bash
python -m uvicorn server.app.examples.fastapi.widgets.button_widget_fastapi:app --host 127.0.0.1 --port 8000
python -m uvicorn server.app.examples.fastapi.widgets.select_widget_fastapi:app --host 127.0.0.1 --port 8000
python -m uvicorn server.app.examples.fastapi.widgets.bar_chart_widget_fastapi:app --host 127.0.0.1 --port 8000
```

Available widget example modules:

- `server.app.examples.fastapi.widgets.accordion_header_widget_fastapi`
- `server.app.examples.fastapi.widgets.accordion_item_widget_fastapi`
- `server.app.examples.fastapi.widgets.accordion_widget_fastapi`
- `server.app.examples.fastapi.widgets.alert_widget_fastapi`
- `server.app.examples.fastapi.widgets.audio_widget_fastapi`
- `server.app.examples.fastapi.widgets.badge_widget_fastapi`
- `server.app.examples.fastapi.widgets.bar_chart_widget_fastapi`
- `server.app.examples.fastapi.widgets.button_widget_fastapi`
- `server.app.examples.fastapi.widgets.card_widget_fastapi`
- `server.app.examples.fastapi.widgets.checkbox_widget_fastapi`
- `server.app.examples.fastapi.widgets.code_block_widget_fastapi`
- `server.app.examples.fastapi.widgets.connection_status_widget_fastapi`
- `server.app.examples.fastapi.widgets.container_widget_fastapi`
- `server.app.examples.fastapi.widgets.date_picker_widget_fastapi`
- `server.app.examples.fastapi.widgets.divider_widget_fastapi`
- `server.app.examples.fastapi.widgets.heading_widget_fastapi`
- `server.app.examples.fastapi.widgets.icon_button_widget_fastapi`
- `server.app.examples.fastapi.widgets.image_widget_fastapi`
- `server.app.examples.fastapi.widgets.label_widget_fastapi`
- `server.app.examples.fastapi.widgets.link_widget_fastapi`
- `server.app.examples.fastapi.widgets.list_view_widget_fastapi`
- `server.app.examples.fastapi.widgets.modal_widget_fastapi`
- `server.app.examples.fastapi.widgets.option_widget_fastapi`
- `server.app.examples.fastapi.widgets.paragraph_widget_fastapi`
- `server.app.examples.fastapi.widgets.progress_widget_fastapi`
- `server.app.examples.fastapi.widgets.row_widget_fastapi`
- `server.app.examples.fastapi.widgets.select_widget_fastapi`
- `server.app.examples.fastapi.widgets.slider_widget_fastapi`
- `server.app.examples.fastapi.widgets.spinner_widget_fastapi`
- `server.app.examples.fastapi.widgets.stack_widget_fastapi`
- `server.app.examples.fastapi.widgets.tab_item_widget_fastapi`
- `server.app.examples.fastapi.widgets.tabs_widget_fastapi`
- `server.app.examples.fastapi.widgets.text_area_widget_fastapi`
- `server.app.examples.fastapi.widgets.text_input_widget_fastapi`
- `server.app.examples.fastapi.widgets.video_widget_fastapi`
- `server.app.examples.fastapi.widgets.window_widget_fastapi`
