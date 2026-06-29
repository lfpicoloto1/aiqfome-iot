from __future__ import annotations

import enum
import random
import time

from src.config import BlinkConfig


class BlinkState(enum.Enum):
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"
    OPENING = "opening"


class BlinkController:
    """State machine that drives natural eye blinking."""

    MIN_SCALE_Y = 0.05

    def __init__(self, config: BlinkConfig) -> None:
        self._base_config = config
        self._interval_mult = 1.0
        self._duration_mult = 1.0
        self._state = BlinkState.OPEN
        self._scale_y = 1.0
        self._state_started_at = time.monotonic()
        self._next_blink_at = self._schedule_next_blink()
        self._double_blink_pending = False

    @property
    def scale_y(self) -> float:
        return self._scale_y

    @property
    def state(self) -> BlinkState:
        return self._state

    def set_timing_multipliers(
        self,
        interval_mult: float,
        duration_mult: float,
    ) -> None:
        self._interval_mult = interval_mult
        self._duration_mult = duration_mult

    def trigger_blink(self) -> None:
        if self._state == BlinkState.OPEN:
            self._enter_state(BlinkState.CLOSING, time.monotonic())

    def update(self) -> None:
        now = time.monotonic()

        if self._state == BlinkState.OPEN:
            if now >= self._next_blink_at:
                self._enter_state(BlinkState.CLOSING, now)
            return

        elapsed_ms = (now - self._state_started_at) * 1000
        close_ms = self._base_config.close_duration_ms * self._duration_mult
        open_ms = self._base_config.open_duration_ms * self._duration_mult

        if self._state == BlinkState.CLOSING:
            progress = min(elapsed_ms / close_ms, 1.0)
            self._scale_y = 1.0 - progress * (1.0 - self.MIN_SCALE_Y)
            if progress >= 1.0:
                self._enter_state(BlinkState.CLOSED, now)
            return

        if self._state == BlinkState.CLOSED:
            self._scale_y = self.MIN_SCALE_Y
            if elapsed_ms >= self._base_config.closed_hold_ms:
                self._enter_state(BlinkState.OPENING, now)
            return

        if self._state == BlinkState.OPENING:
            progress = min(elapsed_ms / open_ms, 1.0)
            self._scale_y = self.MIN_SCALE_Y + progress * (1.0 - self.MIN_SCALE_Y)
            if progress >= 1.0:
                self._enter_state(BlinkState.OPEN, now)
                if self._double_blink_pending:
                    self._double_blink_pending = False
                    self._next_blink_at = now + 0.15
                else:
                    self._next_blink_at = self._schedule_next_blink(now)

    def _enter_state(self, state: BlinkState, now: float) -> None:
        self._state = state
        self._state_started_at = now

        if state == BlinkState.CLOSING and random.random() < self._base_config.double_blink_chance:
            self._double_blink_pending = True

    def _schedule_next_blink(self, now: float | None = None) -> float:
        base = now if now is not None else time.monotonic()
        interval = random.uniform(
            self._base_config.min_interval_s * self._interval_mult,
            self._base_config.max_interval_s * self._interval_mult,
        )
        return base + interval
