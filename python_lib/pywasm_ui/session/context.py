from __future__ import annotations

from dataclasses import dataclass

from pywasm_ui.security import SessionSecurityState
from pywasm_ui.widgets import WidgetTree


@dataclass
class SessionContext:
    security: SessionSecurityState
    tree: WidgetTree
