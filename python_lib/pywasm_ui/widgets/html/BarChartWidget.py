from __future__ import annotations

import json
from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class BarChartWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        values: list[float] | None = None,
        labels: list[str] | None = None,
        max_value: float | None = None,
        width: int = 360,
        height: int = 180,
        title: str = "Bar chart",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        normalized_values = [float(v) for v in (values or [])]
        normalized_labels = [str(label) for label in labels] if labels is not None else []

        attrs: dict[str, str] = {
            "role": "img",
            "aria-label": title,
            "data-chart-values": json.dumps(normalized_values, ensure_ascii=True),
            "data-chart-labels": json.dumps(normalized_labels, ensure_ascii=True),
            "data-chart-width": str(max(120, int(width))),
            "data-chart-height": str(max(120, int(height))),
        }
        if max_value is not None:
            attrs["data-chart-max"] = str(float(max_value))

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="div",
            defaults={
                "attrs": attrs,
                "classes": ["bar-chart-widget"],
            },
            props=props,
            style=style,
        )
