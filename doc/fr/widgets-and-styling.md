# Widgets et Style

## Widgets standards

- `WindowWidget`
- `ContainerWidget`
- `LabelWidget`
- `ButtonWidget`
- `TextInputWidget`
- `ListViewWidget`
- `ConnectionStatusWidget`

Chaque widget expose:

- `id`
- `kind`
- `parent`
- `props`
- `children`
- `style` (objet `Style` synchronise avec `props["style"]`)

## Style pythonique

```python
from pywasm_ui import ButtonWidget

button = ButtonWidget(id="btn1", text="OK")
button.style.set(font_size="16px", background_color="#0ea5e9")
button.style.set("border-radius", "8px")
button.style.remove("background-color")
```

Regles:

- `snake_case` -> `kebab-case`
- conversion automatique des valeurs en string
- suppression via `remove(...)` ou `set(..., None)`

## Patching conseille

```python
from pywasm_ui import merge_patches, patch_text, patch_style

patch = merge_patches(
    "label1",
    patch_text("label1", "Updated"),
    patch_style("label1", {"font_weight": "700", "color": "#111"}),
)
```

## Cote client WASM

Le runtime applique:

- `text`
- `value`
- `enabled`
- `classes`
- `attrs` / `remove_attrs`
- `style`
