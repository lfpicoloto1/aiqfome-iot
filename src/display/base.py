from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pygame


@dataclass(frozen=True)
class InputState:
    running: bool
    touches: tuple[tuple[int, int], ...] = ()


class DisplayBackend(Protocol):
    def get_surface(self) -> pygame.Surface: ...

    def flip(self) -> None: ...

    def tick(self, fps: int) -> None: ...

    def handle_events(self) -> InputState:
        """Process input events and return running state plus touch points."""
        ...

    def quit(self) -> None: ...
