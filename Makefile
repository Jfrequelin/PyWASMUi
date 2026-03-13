.PHONY: setup server wasm run-fastapi-single run-flask-single poetry-install poetry-build poetry-publish-testpypi poetry-publish-pypi

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

poetry-install:
	cd python_lib && poetry install

poetry-build:
	cd python_lib && poetry build

poetry-publish-testpypi: poetry-build
	cd python_lib && poetry publish --repository testpypi

poetry-publish-pypi: poetry-build
	cd python_lib && poetry publish
