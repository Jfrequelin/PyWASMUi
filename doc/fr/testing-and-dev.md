# Tests et Developpement

## Chemin Rapide De Test Apres Clone

```bash
python -m pip install -r requirements-test.txt

# smoke tests rapides
python -m pytest tests/unit/test_widgets.py tests/integration/test_fastapi_websocket.py

# suite complete
python -m pytest
```

Catalogue Selenium optionnel (Chrome requis):

```bash
python -m pytest tests/integration/test_selenium_widgets_catalog.py -q
```

## Lancer tous les tests

```bash
python -m pytest
```

## Perimetre couvert

- tests unitaires: `tests/unit/`
- tests integration: `tests/integration/`

La suite couvre notamment:

- cycle session (`init`, reconnect, replay)
- protocole WebSocket
- widgets et payloads
- helpers patch (`patch_style` inclus)

## Build WASM

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```

## Boucle dev recommandee

1. Modifier le code Python ou Rust.
2. Executer `pytest`.
3. Rebuild WASM si le runtime Rust a change.
4. Relancer FastAPI si necessaire.
5. Tester dans le navigateur.

## Depannage ports

```bash
fuser -k 8000/tcp || true
fuser -k 5173/tcp || true
```

Verification serveur:

```bash
curl -sS http://127.0.0.1:8000/health
```
