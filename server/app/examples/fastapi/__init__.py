"""FastAPI example entrypoints."""

import importlib

from .all_widgets_fastapi import app as all_widgets_app
from .fastapi_server import app

example_01_app = importlib.import_module(
	".01_single_widget_fastapi",
	package=__name__,
).app
example_02_app = importlib.import_module(
	".02_widget_composition_fastapi",
	package=__name__,
).app
example_03_app = importlib.import_module(
	".03_style_updates_fastapi",
	package=__name__,
).app
example_05_app = importlib.import_module(
	".05_form_controls_fastapi",
	package=__name__,
).app
example_10_app = importlib.import_module(
	".10_widgets_catalog_fastapi",
	package=__name__,
).app

__all__ = [
	"app",
	"all_widgets_app",
	"example_01_app",
	"example_02_app",
	"example_03_app",
	"example_05_app",
	"example_10_app",
]
