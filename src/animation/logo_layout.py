from __future__ import annotations

from dataclasses import dataclass

# Measured from assets/logo-reference.png (official aiqfome logo, icon only).
LOGO_ICON_WIDTH = 172
LOGO_EYE_WIDTH = 21
LOGO_EYE_HEIGHT = 38
LOGO_EYE_GAP = 48  # space between inner edges at horizontal midline
LOGO_EYE_WIDTH_FRAC = LOGO_EYE_WIDTH / LOGO_ICON_WIDTH
LOGO_EYE_GAP_RATIO = LOGO_EYE_GAP / LOGO_EYE_WIDTH
LOGO_EYE_HEIGHT_RATIO = LOGO_EYE_HEIGHT / LOGO_EYE_WIDTH


@dataclass(frozen=True)
class LogoEyeLayout:
    width: int
    height: int
    gap: int
    center_y: int
    gap_ratio: float


def layout_for_screen(screen_width: int, screen_height: int) -> LogoEyeLayout:
    """Scale logo eye geometry to the LCD so spacing matches the official icon."""
    width = max(round(LOGO_EYE_WIDTH_FRAC * screen_width), 8)
    height = max(round(width * LOGO_EYE_HEIGHT_RATIO), 8)
    gap = max(round(width * LOGO_EYE_GAP_RATIO), 2)
    # Viewport vertical center for the LCD cutout (face window, not full icon).
    center_y = max(round(screen_height * 0.42), height // 2)
    return LogoEyeLayout(
        width=width,
        height=height,
        gap=gap,
        center_y=center_y,
        gap_ratio=LOGO_EYE_GAP_RATIO,
    )
