from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EyePose:
    """Rendered eye state for one frame."""

    offset_x: float = 0.0
    offset_y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    color: tuple[int, int, int] = (255, 255, 255)
