# FastAPI Example Series

Progressive examples to learn pyWasm usage patterns.

## 01. Single widget

File: `server/app/examples/fastapi/01_single_widget_fastapi.py`

Run:

```bash
/home/rlv/.pyenv/versions/3.11.14/bin/python -m uvicorn server.app.examples.fastapi.01_single_widget_fastapi:app --host 127.0.0.1 --port 8000
```

## 02. Widget composition (parent/child)

File: `server/app/examples/fastapi/02_widget_composition_fastapi.py`

Run:

```bash
/home/rlv/.pyenv/versions/3.11.14/bin/python -m uvicorn server.app.examples.fastapi.02_widget_composition_fastapi:app --host 127.0.0.1 --port 8000
```

## 03. Style update at runtime

File: `server/app/examples/fastapi/03_style_updates_fastapi.py`

Run:

```bash
/home/rlv/.pyenv/versions/3.11.14/bin/python -m uvicorn server.app.examples.fastapi.03_style_updates_fastapi:app --host 127.0.0.1 --port 8000
```

## 04. Shared template reused across apps

File: `server/app/examples/fastapi/04_style_template_fastapi.py`

Template file: `server/app/examples/fastapi/shared_style_template.json`

Run:

```bash
/home/rlv/.pyenv/versions/3.11.14/bin/python -m uvicorn server.app.examples.fastapi.04_style_template_fastapi:app --host 127.0.0.1 --port 8000
```
