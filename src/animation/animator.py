from __future__ import annotations

import time

from src.animation.blink import BlinkController
from src.animation.easing import clamp, lerp
from src.animation.mood import MoodController
from src.animation.pose import EyePose
from src.config import AppConfig, hex_to_rgb


class EyeAnimator:
    """Combines blinking, mood states, touch reactions, and color fade."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._blink = BlinkController(config.blink)
        self._mood = MoodController(config.animation)
        self._base_eye_color = hex_to_rgb(config.colors.eyes)
        self._bg_color = hex_to_rgb(config.colors.background)

        self._touch_offset_x = 0.0
        self._touch_offset_y = 0.0
        self._touch_offset_target_x = 0.0
        self._touch_offset_target_y = 0.0
        self._touch_glance_started_at = time.monotonic()

    def on_touch(self, x: int, y: int) -> None:
        center_x = self._config.display.width // 2
        max_x = self._config.animation.touch_glance_max_x
        max_y = self._config.animation.touch_glance_max_y
        factor = self._config.animation.touch_glance_factor

        self._touch_offset_target_x = clamp((x - center_x) * factor, -max_x, max_x)
        self._touch_offset_target_y = clamp(
            (y - self._config.eyes.center_y) * factor,
            -max_y,
            max_y,
        )
        self._touch_glance_started_at = time.monotonic()
        self._blink.trigger_blink()

    def update(self) -> EyePose:
        self._mood.update()
        mood = self._mood.params()
        self._blink.set_timing_multipliers(
            mood.blink_interval_mult,
            mood.blink_duration_mult,
        )
        self._blink.update()
        self._update_touch_glance()

        look_x, look_y = self._mood.look_offset()
        offset_x = look_x + self._touch_offset_x
        offset_y = look_y + self._touch_offset_y

        scale_y = mood.scale_y * self._blink.scale_y
        color = self._eye_color(mood.color_brightness)

        return EyePose(
            offset_x=offset_x,
            offset_y=offset_y,
            scale_x=mood.scale_x,
            scale_y=scale_y,
            color=color,
        )

    def _update_touch_glance(self) -> None:
        now = time.monotonic()
        elapsed_ms = (now - self._touch_glance_started_at) * 1000
        hold_ms = self._config.animation.touch_glance_hold_ms
        return_ms = self._config.animation.touch_glance_return_ms

        if elapsed_ms <= hold_ms:
            self._touch_offset_x = self._touch_offset_target_x
            self._touch_offset_y = self._touch_offset_target_y
            return

        return_elapsed = elapsed_ms - hold_ms
        if return_elapsed >= return_ms:
            self._touch_offset_x = 0.0
            self._touch_offset_y = 0.0
            self._touch_offset_target_x = 0.0
            self._touch_offset_target_y = 0.0
            return

        t = return_elapsed / return_ms
        self._touch_offset_x = lerp(self._touch_offset_target_x, 0.0, t)
        self._touch_offset_y = lerp(self._touch_offset_target_y, 0.0, t)

    def _eye_color(self, brightness: float) -> tuple[int, int, int]:
        r, g, b = self._base_eye_color
        br, bg, bb = self._bg_color
        t = 1.0 - brightness
        return (
            int(r * brightness + br * t),
            int(g * brightness + bg * t),
            int(b * brightness + bb * t),
        )
