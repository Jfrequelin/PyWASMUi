from __future__ import annotations

from pywasm_ui import (
    Style,
    merge_patches,
    patch_attrs,
    patch_classes,
    patch_enabled,
    patch_style,
    patch_value,
    set_text,
)


def test_patch_helpers_and_merge() -> None:
    p = merge_patches(
        "label1",
        set_text("label1", "Ready"),
        patch_enabled("label1", True),
        patch_classes("label1", ["primary"]),
        patch_attrs("label1", {"data-x": 1}),
        patch_style("label1", Style(font_size="12px", margin_top="4px")),
        patch_value("label1", "ignored-by-label"),
    )

    assert p["id"] == "label1"
    assert p["text"] == "Ready"
    assert p["enabled"] is True
    assert p["classes"] == ["primary"]
    assert p["attrs"]["data-x"] == 1
    assert p["style"]["font-size"] == "12px"
    assert p["style"]["margin-top"] == "4px"
    assert p["value"] == "ignored-by-label"


def test_patch_style_accepts_raw_dict() -> None:
    patch = patch_style("label1", {"line_height": "1.5", "opacity": 0.9})

    assert patch["id"] == "label1"
    assert patch["style"]["line-height"] == "1.5"
    assert patch["style"]["opacity"] == "0.9"


def test_patch_style_accepts_css_text_and_kwargs() -> None:
    patch = patch_style(
        "label1",
        "color: #222; margin-top: 4px",
        font_weight=700,
    )

    assert patch["id"] == "label1"
    assert patch["style"]["color"] == "#222"
    assert patch["style"]["margin-top"] == "4px"
    assert patch["style"]["font-weight"] == "700"
