from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, TypeAlias

from pywasm_ui.widgets import WasmWidget

if TYPE_CHECKING:
    from pywasm_ui.session import PyWasmSession


ComponentNode: TypeAlias = "WasmWidget | Component | Sequence[ComponentNode]"


class Component(ABC):
    """Composable Python-side UI unit inspired by high-level frameworks.

    A component can return one widget, a nested list of widgets, other
    components, or a mix of all of them.
    """

    @abstractmethod
    def build(self, session: "PyWasmSession") -> ComponentNode:
        """Build this component into widgets/components for a session."""


def render_component_widgets(node: ComponentNode, session: "PyWasmSession") -> list[WasmWidget]:
    """Resolve a component tree into a flat widget list."""

    out: list[WasmWidget] = []

    def visit(current: ComponentNode) -> None:
        if isinstance(current, WasmWidget):
            out.append(current)
            return

        if isinstance(current, Component):
            visit(current.build(session))
            return

        if isinstance(current, Sequence) and not isinstance(current, (str, bytes, bytearray)):
            for child in current:
                visit(child)
            return

        raise TypeError(f"Unsupported component node type: {type(current)!r}")

    visit(node)
    return out
