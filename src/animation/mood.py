from __future__ import annotations

import enum
import random
import time
from dataclasses import dataclass

from src.animation.easing import ease_in_out, lerp
from src.config import AnimationConfig


class Mood(enum.Enum):
    IDLE = "idle"
    CURIOUS = "curious"
    SLEEPY = "sleepy"
    ALERT = "alert"


@dataclass(frozen=True)
class MoodParams:
    scale_x: float
    scale_y: float
    color_brightness: float
    blink_interval_mult: float
    blink_duration_mult: float


class LookPhase(enum.Enum):
    CENTER = "center"
    MOVING = "moving"
    HOLD = "hold"
    RETURNING = "returning"


@dataclass
class _LookTarget:
    offset_x: float
    offset_y: float


class MoodController:
    """Cycles through moods and drives look-at animations without changing eye gap."""

    def __init__(self, config: AnimationConfig) -> None:
        self._config = config
        self._mood = Mood.IDLE
        self._mood_started_at = time.monotonic()
        self._mood_duration = self._pick_duration(Mood.IDLE)

        self._look_phase = LookPhase.CENTER
        self._look_started_at = time.monotonic()
        self._look_from = _LookTarget(0.0, 0.0)
        self._look_to = _LookTarget(0.0, 0.0)
        self._look_current = _LookTarget(0.0, 0.0)
        self._next_look_at = time.monotonic() + random.uniform(1.0, 2.5)
        self._look_hold_until = 0.0

    @property
    def mood(self) -> Mood:
        return self._mood

    def params(self) -> MoodParams:
        profiles = {
            Mood.IDLE: MoodParams(1.0, 1.0, 1.0, 1.0, 1.0),
            Mood.CURIOUS: MoodParams(1.0, 1.0, 1.0, 0.9, 1.0),
            Mood.SLEEPY: MoodParams(1.0, 0.58, 0.82, 1.6, 1.5),
            Mood.ALERT: MoodParams(1.06, 1.06, 1.0, 1.4, 1.0),
        }
        return profiles[self._mood]

    def look_offset(self) -> tuple[float, float]:
        return self._look_current.offset_x, self._look_current.offset_y

    def update(self) -> None:
        now = time.monotonic()
        if now - self._mood_started_at >= self._mood_duration:
            self._switch_mood(now)

        if self._mood == Mood.CURIOUS:
            self._update_curious_look(now)
        else:
            self._ease_look_toward(0.0, 0.0, now, self._config.look_return_ms)

    def _switch_mood(self, now: float) -> None:
        choices = [m for m in Mood if m != self._mood]
        self._mood = random.choice(choices)
        self._mood_started_at = now
        self._mood_duration = self._pick_duration(self._mood)
        self._look_phase = LookPhase.CENTER
        self._look_current = _LookTarget(0.0, 0.0)
        self._next_look_at = now + random.uniform(0.8, 2.0)

    def _pick_duration(self, mood: Mood) -> float:
        ranges = {
            Mood.IDLE: (self._config.idle_min_s, self._config.idle_max_s),
            Mood.CURIOUS: (self._config.curious_min_s, self._config.curious_max_s),
            Mood.SLEEPY: (self._config.sleepy_min_s, self._config.sleepy_max_s),
            Mood.ALERT: (self._config.alert_min_s, self._config.alert_max_s),
        }
        low, high = ranges[mood]
        return random.uniform(low, high)

    def _update_curious_look(self, now: float) -> None:
        if self._look_phase == LookPhase.CENTER and now >= self._next_look_at:
            direction = random.choice(
                [
                    _LookTarget(-self._config.look_offset_x, 0.0),
                    _LookTarget(self._config.look_offset_x, 0.0),
                    _LookTarget(0.0, -self._config.look_offset_y),
                    _LookTarget(0.0, self._config.look_offset_y),
                ]
            )
            self._look_from = _LookTarget(
                self._look_current.offset_x,
                self._look_current.offset_y,
            )
            self._look_to = direction
            self._look_phase = LookPhase.MOVING
            self._look_started_at = now
            return

        elapsed_ms = (now - self._look_started_at) * 1000

        if self._look_phase == LookPhase.MOVING:
            progress = ease_in_out(elapsed_ms / self._config.look_move_ms)
            self._look_current = _LookTarget(
                lerp(self._look_from.offset_x, self._look_to.offset_x, progress),
                lerp(self._look_from.offset_y, self._look_to.offset_y, progress),
            )
            if progress >= 1.0:
                self._look_phase = LookPhase.HOLD
                self._look_started_at = now
                hold_ms = random.uniform(
                    self._config.look_hold_min_ms,
                    self._config.look_hold_max_ms,
                )
                self._look_hold_until = now + hold_ms / 1000.0
            return

        if self._look_phase == LookPhase.HOLD:
            if now >= self._look_hold_until:
                self._look_from = _LookTarget(
                    self._look_current.offset_x,
                    self._look_current.offset_y,
                )
                self._look_to = _LookTarget(0.0, 0.0)
                self._look_phase = LookPhase.RETURNING
                self._look_started_at = now
            return

        if self._look_phase == LookPhase.RETURNING:
            progress = ease_in_out(elapsed_ms / self._config.look_return_ms)
            self._look_current = _LookTarget(
                lerp(self._look_from.offset_x, 0.0, progress),
                lerp(self._look_from.offset_y, 0.0, progress),
            )
            if progress >= 1.0:
                self._look_phase = LookPhase.CENTER
                self._look_current = _LookTarget(0.0, 0.0)
                self._next_look_at = now + random.uniform(1.0, 2.5)

    def _ease_look_toward(
        self,
        target_x: float,
        target_y: float,
        now: float,
        duration_ms: float,
    ) -> None:
        if (
            abs(self._look_current.offset_x - target_x) < 0.1
            and abs(self._look_current.offset_y - target_y) < 0.1
        ):
            self._look_current = _LookTarget(target_x, target_y)
            return

        if self._look_phase not in (LookPhase.RETURNING, LookPhase.MOVING):
            self._look_from = _LookTarget(
                self._look_current.offset_x,
                self._look_current.offset_y,
            )
            self._look_to = _LookTarget(target_x, target_y)
            self._look_phase = LookPhase.RETURNING
            self._look_started_at = now

        elapsed_ms = (now - self._look_started_at) * 1000
        progress = ease_in_out(elapsed_ms / duration_ms)
        self._look_current = _LookTarget(
            lerp(self._look_from.offset_x, target_x, progress),
            lerp(self._look_from.offset_y, target_y, progress),
        )
        if progress >= 1.0:
            self._look_phase = LookPhase.CENTER
