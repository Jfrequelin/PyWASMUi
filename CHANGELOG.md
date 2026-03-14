# Changelog

All notable changes to this project will be documented in this file.

## [2026-03-14] - Tabs and Accordion Widgets

### Added
- Added new HTML widget classes for tabbed and accordion interfaces:
  - `python_lib/pywasm_ui/widgets/html/TabsWidget.py`
  - `python_lib/pywasm_ui/widgets/html/TabItemWidget.py`
  - `python_lib/pywasm_ui/widgets/html/AccordionWidget.py`
  - `python_lib/pywasm_ui/widgets/html/AccordionItemWidget.py`
  - `python_lib/pywasm_ui/widgets/html/AccordionHeaderWidget.py`
- Exported the new widgets in:
  - `python_lib/pywasm_ui/widgets/html/__init__.py`
  - `python_lib/pywasm_ui/widgets/__init__.py`
  - `python_lib/pywasm_ui/__init__.py`

### Changed
- Extended the example catalog in `server/app/examples/fastapi/10_widgets_catalog_fastapi.py` with a dedicated section demonstrating tabs and accordion usage.
- Extended widget unit coverage in `tests/unit/test_widgets.py` for payload structure, events, and kind-convention checks of the new widgets.

## [2026-03-14] - Automatic Theme Loading for Example 10

### Added
- Added automatic theme discovery in `server/app/examples/fastapi/10_widgets_catalog_fastapi.py` by scanning `server/app/examples/web/themes/*.css` (excluding `base.css`) and generating `theme_select` options dynamically.
- Added dynamic stylesheet loading in `server/app/examples/web/index.html` so the active theme CSS is loaded from `/themes/<theme>.css` at runtime.

### Changed
- Updated example 10 theme options to no longer rely on a hard-coded list in Python.
- Updated the page stylesheet bootstrap to load `base.css` directly and resolve the selected theme through a dedicated dynamic `<link>` element.

## [2026-03-14] - Simplified API Rollout in Docs and Examples

### Added
- Added one-call app bootstrap helpers in adapter layer:
  - `bootstrap_fastapi_app(...)`
  - `bootstrap_flask_app(...)`
- Added adapter facade shortcuts:
  - `pywasm_ui.fastapi.bootstrap_app(...)`
  - `pywasm_ui.flask.bootstrap_app(...)`
- Added public exports for simplified helpers in `python_lib/pywasm_ui/__init__.py`.

### Changed
- Migrated FastAPI and Flask main examples to simplified bootstrap wiring:
  - `server/app/examples/fastapi/fastapi_server.py`
  - `server/app/examples/flask/flask_server.py`
- Migrated FastAPI tutorial/showcase examples from 3-step wiring to one-call bootstrap:
  - `server/app/examples/fastapi/01_single_widget_fastapi.py`
  - `server/app/examples/fastapi/02_widget_composition_fastapi.py`
  - `server/app/examples/fastapi/03_style_updates_fastapi.py`
  - `server/app/examples/fastapi/05_form_controls_fastapi.py`
  - `server/app/examples/fastapi/10_widgets_catalog_fastapi.py`
  - `server/app/examples/fastapi/all_widgets_fastapi.py`
- Updated documentation to make simplified bootstrap integration the recommended path while keeping low-level helpers documented:
  - `README.md`
  - `python_lib/README.md`
  - `doc/en/getting-started.md`
  - `doc/fr/getting-started.md`
  - `doc/en/python-api.md`
  - `doc/fr/python-api.md`

### Tests
- Extended adapter coverage with a dedicated simplified bootstrap test in `tests/unit/test_adapters.py`.

## [2026-03-13] - Open Source Readiness Pack

### Added
- Added project license file `LICENSE` (MIT).
- Added contribution and governance documents:
  - `CONTRIBUTING.md`
  - `CODE_OF_CONDUCT.md`
  - `SECURITY.md`
- Added GitHub collaboration templates:
  - `.github/ISSUE_TEMPLATE/bug_report.yml`
  - `.github/ISSUE_TEMPLATE/feature_request.yml`
  - `.github/pull_request_template.md`

## [2026-03-13] - Poetry Packaging and CI Reliability Updates

### Added
- Added Poetry lockfile `python_lib/poetry.lock` and Poetry-based packaging workflow.
- Added PyPI publish workflow `/.github/workflows/pypi-publish.yml`.

### Changed
- Migrated Python package build configuration in `python_lib/pyproject.toml` to `poetry-core` backend.
- Added Makefile targets for Poetry install/build/publish (`poetry-install`, `poetry-build`, `poetry-publish-*`).
- Updated release workflow to build Python distributions with Poetry.
- Updated docs for Poetry/PyPI usage in:
  - `README.md`
  - `python_lib/README.md`
  - `doc/fr/getting-started.md`
- Fixed WASM event signing by restoring HMAC `mac` generation in client runtime (`client/wasm_ui/src/*`) and rebuilt packaged WASM assets.
- Hardened Selenium integration tests to reduce flaky click and async timing failures.
- Stabilized strict pylint gate via test hardening and lint configuration alignment.

## [2026-03-13] - Widget Catalog, Themes, and Security Hardening

### Added
- Added new FastAPI example `server/app/examples/fastapi/10_widgets_catalog_fastapi.py` with a full widget catalog and interactive flows.
- Added reusable widget tooltip API in `python_lib/pywasm_ui/widgets/base.py` via `WasmWidget.tooltip(...)`.
- Added dedicated theme files under `server/app/examples/web/themes/`:
  - `base.css`
  - `modern.css`
  - `slate.css`
  - `sunset.css`
  - `neo-ember.css`
  - `ladys.css`
- Added `server/app/examples/web/theme-modern.css` as CSS entrypoint importing split theme files.
- Added/updated tests for tooltip behavior and adapter helpers:
  - `tests/unit/test_widgets.py`
  - `tests/unit/test_session.py`
  - `tests/unit/test_adapters.py`
  - `tests/integration/test_fastapi_websocket.py`

### Changed
- Refactored frontend styling to use modular theme files instead of a monolithic stylesheet.
- Updated `server/app/examples/web/index.html` to use the external stylesheet entrypoint and cache-busted runtime assets.
- Expanded event handling support across session/runtime (multi-event wiring and normalized event metadata).
- Updated examples and docs to include the new catalog flow and revised example mapping (`server/app/examples/fastapi/EXAMPLES.md`).

### Security
- Enforced signed WebSocket events: missing `mac` now rejected (`missing-mac`) in `python_lib/pywasm_ui/session/core.py`.
- Kept nonce validation strict for replay protection.
- Added session pruning controls in adapters (TTL and max active sessions):
  - `PYWASM_SESSION_TTL_SECONDS`
  - `PYWASM_MAX_ACTIVE_SESSIONS`
- Added optional WebSocket origin allow-list support:
  - `PYWASM_ALLOWED_WS_ORIGINS`
- Added default security headers on frontend responses (including CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy) with CSP adjusted for inline bootstrap + WebAssembly runtime compatibility.

### Removed
- Removed obsolete example/template artifacts:
  - `server/app/examples/fastapi/04_style_template_fastapi.py`
  - `server/app/examples/fastapi/shared_style_template.json`

## [2026-03-11] - Rio-Inspired API and Example Rewrite

### Added
- Added a Rio-inspired Python API surface across core modules (`components`, `events`, `routing`, `theme`, `widgets`).

### Changed
- Reworked example and API documentation in both English and French to align with the new API direction.
- Updated many HTML widget implementations and session/adapters integration for the rewritten examples.

## [2026-03-10] - Branding and Example Refactor

### Changed
- Normalized product naming to `PyWASMui` across docs, examples, runtime config, and integration tests.
- Refactored `server/app/examples/fastapi/all_widgets_fastapi.py` structure for clearer organization and maintenance.

## [2026-03-09] - Packaging, Docs Refresh, and CI Stabilization

### Added
- Added release workflow automation via `.github/workflows/main.yml`.
- Added support for packaged frontend assets in Python distribution (`python_lib/pyproject.toml`, `frontend_assets.py`, prebuilt WASM package files).

### Changed
- Refreshed FR/EN documentation sets (architecture, getting-started, API, testing, widgets, protocol).
- Expanded and refactored all-widgets FastAPI example coverage, including browser catalog validation paths.
- Improved dependency stability and CI setup for browser tests and lint/pylint gates.

## [2026-03-08] - CI Bootstrap and Runtime Robustness

### Added
- Introduced initial GitHub Actions CI pipeline for Python tests and WASM build (`.github/workflows/ci.yml`).

### Changed
- Hardened CI dependency installation for FastAPI/Flask extras, Playwright Chromium, and test prerequisites.
- Updated browser integration tests to rely on `sys.executable` and added `httpx` where required for FastAPI TestClient.
- Avoided hard-coded WebSocket fallback URL in `client/src/main.js`.

### Removed
- Removed obsolete prompt and generated metadata files from the repository.
