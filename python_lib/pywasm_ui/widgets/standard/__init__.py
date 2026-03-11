"""Backward-compatible alias for the HTML widget package."""

from importlib import import_module
import sys

from ..html import *  # noqa: F403
from ..html import __all__

# Keep direct submodule imports working, e.g.
# `from pywasm_ui.widgets.standard.ButtonWidget import ButtonWidget`.
_LEGACY_MODULES = [
    "_common",
    "AlertWidget",
    "BadgeWidget",
    "ButtonWidget",
    "CardWidget",
    "CheckboxWidget",
    "ContainerWidget",
    "DatePickerWidget",
    "DividerWidget",
    "HeadingWidget",
    "IconButtonWidget",
    "LabelWidget",
    "ListViewWidget",
    "ModalWidget",
    "OptionWidget",
    "ParagraphWidget",
    "ProgressWidget",
    "RowWidget",
    "SelectWidget",
    "SliderWidget",
    "StackWidget",
    "TextAreaWidget",
    "TextInputWidget",
    "WindowWidget",
]

for _name in _LEGACY_MODULES:
    sys.modules[f"{__name__}.{_name}"] = import_module(f"..html.{_name}", package=__name__)
