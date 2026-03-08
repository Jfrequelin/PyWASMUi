.PHONY: setup server wasm run-fastapi-single run-flask-single

PYTHON ?= python3

setup:
	@echo "No additional setup required."

wasm:
	cd client/wasm_ui && wasm-pack build --target web --out-dir pkg

server:
	cd server && uvicorn app.examples.fastapi.fastapi_server:app --reload --host 127.0.0.1 --port 8000

run-fastapi-single: wasm
	$(PYTHON) -m uvicorn server.app.examples.fastapi.fastapi_server:app --host 127.0.0.1 --port 8000

run-flask-single: wasm
	cd server && $(PYTHON) -c "from app.examples.flask.flask_server import run; run()"
