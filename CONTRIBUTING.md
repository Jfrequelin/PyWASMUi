# Contributing to PyWASMui

Thanks for your interest in contributing.

## Getting Started

1. Fork the repository and create a branch from `main`.
2. Use Python 3.11.
3. Install dependencies:

```bash
python -m pip install -r requirements-test.txt
python -m pip install -e python_lib
```

## Development Workflow

1. Make focused changes with clear commit messages.
2. Add or update tests when behavior changes.
3. Run checks before opening a PR:

```bash
python -m pytest
```

If you work on WASM code:

```bash
cd client/wasm_ui
wasm-pack build --target web --out-dir pkg
```

## Pull Request Guidelines

- Keep PRs small and focused.
- Include context: what changed and why.
- Reference related issues when possible.
- Ensure CI is green.

## Coding Style

- Follow existing project style.
- Prefer readable code over clever code.
- Keep public-facing behavior documented in README/changelog when relevant.

## Reporting Bugs

Please use the bug report template and include:

- reproduction steps,
- expected behavior,
- actual behavior,
- environment details.
