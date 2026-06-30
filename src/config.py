from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.animation.logo_layout import layout_for_screen


@dataclass(frozen=True)
class DisplayConfig:
    width: int
    height: int
    fps: int
    rotation: int
    fullscreen: bool = False


@dataclass(frozen=True)
class ColorsConfig:
    background: str
    eyes: str


@dataclass(frozen=True)
class EyesConfig:
    center_y: int
    width: int
    height: int
    gap_ratio: float
    from_logo: bool = True
    center_y_offset: int = 0

    @property
    def gap(self) -> int:
        return round(self.width * self.gap_ratio)


@dataclass(frozen=True)
class BlinkConfig:
    min_interval_s: float
    max_interval_s: float
    close_duration_ms: int
    open_duration_ms: int
    closed_hold_ms: int
    double_blink_chance: float


@dataclass(frozen=True)
class AnimationConfig:
    idle_min_s: float
    idle_max_s: float
    curious_min_s: float
    curious_max_s: float
    sleepy_min_s: float
    sleepy_max_s: float
    alert_min_s: float
    alert_max_s: float
    look_offset_x: float
    look_offset_y: float
    look_move_ms: float
    look_return_ms: float
    look_hold_min_ms: float
    look_hold_max_ms: float
    touch_glance_factor: float
    touch_glance_max_x: float
    touch_glance_max_y: float
    touch_glance_hold_ms: float
    touch_glance_return_ms: float


@dataclass(frozen=True)
class AppConfig:
    display: DisplayConfig
    colors: ColorsConfig
    eyes: EyesConfig
    blink: BlinkConfig
    animation: AnimationConfig


def _resolve_eyes(data: dict[str, Any], display: DisplayConfig) -> EyesConfig:
    from_logo = data.get("from_logo", True)
    center_y_offset = int(data.get("center_y_offset", 0))

    if from_logo:
        layout = layout_for_screen(display.width, display.height)
        return EyesConfig(
            width=layout.width,
            height=layout.height,
            gap_ratio=layout.gap_ratio,
            center_y=layout.center_y + center_y_offset,
            from_logo=True,
            center_y_offset=center_y_offset,
        )

    return EyesConfig(
        center_y=int(data["center_y"]),
        width=int(data["width"]),
        height=int(data["height"]),
        gap_ratio=float(data.get("gap_ratio", 2.286)),
        from_logo=False,
        center_y_offset=center_y_offset,
    )


def load_config(path: Path | str) -> AppConfig:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    display = DisplayConfig(**data["display"])

    return AppConfig(
        display=display,
        colors=ColorsConfig(**data["colors"]),
        eyes=_resolve_eyes(data["eyes"], display),
        blink=BlinkConfig(**data["blink"]),
        animation=AnimationConfig(**data["animation"]),
    )


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
