# Widgets and Styling

## Standard Widgets

- `WindowWidget`
- `ContainerWidget`
- `LabelWidget`
- `ButtonWidget`
- `TextInputWidget`
- `ListViewWidget`
- `ConnectionStatusWidget`

Each widget exposes:

- `id`
- `kind`
- `parent`
- `props`
- `children`
- `style` (`Style` object synchronized with `props["style"]`)

## Pythonic Styling

```python
from pywasm_ui import ButtonWidget

button = ButtonWidget(id="btn1", text="OK")
button.style.set(font_size="16px", background_color="#0ea5e9")
button.style.set("border-radius", "8px")
button.style.remove("background-color")
```

Rules:

- `snake_case` -> `kebab-case`
- values are normalized to string
- remove style with `remove(...)` or `set(..., None)`

## Recommended Patching

```python
from pywasm_ui import merge_patches, patch_text, patch_style

patch = merge_patches(
    "label1",
    patch_text("label1", "Updated"),
    patch_style("label1", {"font_weight": "700", "color": "#111"}),
)
```

## WASM Runtime Application

The client runtime applies:

- `text`
- `value`
- `enabled`
- `classes`
- `attrs` / `remove_attrs`
- `style`
