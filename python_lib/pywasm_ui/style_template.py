from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pywasm_ui.widgets.base import style_dict


@dataclass
class StyleTemplate:
    """Reusable cascading style template shared across applications."""

    by_kind: dict[str, dict[str, str]] = field(default_factory=dict)
    by_class: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StyleTemplate":
        kind_payload = payload.get("by_kind")
        class_payload = payload.get("by_class")

        by_kind: dict[str, dict[str, str]] = {}
        if isinstance(kind_payload, dict):
            for kind, style in kind_payload.items():
                if not isinstance(kind, str):
                    continue
                normalized = style_dict(style)
                if normalized:
                    by_kind[kind] = normalized

        by_class: dict[str, dict[str, str]] = {}
        if isinstance(class_payload, dict):
            for class_name, style in class_payload.items():
                if not isinstance(class_name, str):
                    continue
                normalized = style_dict(style)
                if normalized:
                    by_class[class_name] = normalized

        return cls(by_kind, by_class)

    def to_dict(self) -> dict[str, Any]:
        return {
            "by_kind": self.by_kind,
            "by_class": self.by_class,
        }

    @classmethod
    def load(cls, path: str | Path) -> "StyleTemplate":
        file_path = Path(path)
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("StyleTemplate file must contain a JSON object")
        return cls.from_dict(payload)

    def save(self, path: str | Path) -> Path:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return file_path

    def set_kind(self, kind: str, style: dict[str, Any] | str) -> "StyleTemplate":
        normalized = style_dict(style)
        if normalized:
            self.by_kind[kind] = normalized
        return self

    def set_class(self, class_name: str, style: dict[str, Any] | str) -> "StyleTemplate":
        normalized = style_dict(style)
        if normalized:
            self.by_class[class_name] = normalized
        return self
