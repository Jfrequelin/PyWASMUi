# Widgets et Style

## Widgets standards

- `WindowWidget`
- `ContainerWidget`
- `CardWidget`
- `StackWidget`
- `RowWidget`
- `HeadingWidget`
- `ParagraphWidget`
- `DividerWidget`
- `BadgeWidget`
- `AlertWidget`
- `LabelWidget`
- `ButtonWidget`
- `TextInputWidget`
- `TextAreaWidget`
- `SliderWidget`
- `SelectWidget`
- `OptionWidget`
- `CheckboxWidget`
- `DatePickerWidget`
- `ProgressWidget`
- `ModalWidget`
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
from pywasm_ui import merge_patches, set_text, patch_style

patch = merge_patches(
    "label1",
    set_text("label1", "Updated"),
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

## Verification integration

- Selenium unitaire par widget: `tests/integration/test_selenium_widgets_catalog.py`
- Selenium scenarios exemples: `tests/integration/test_selenium_examples.py`
