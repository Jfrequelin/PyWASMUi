# Changelog

All notable changes to this project will be documented in this file.

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
