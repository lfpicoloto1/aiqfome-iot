from __future__ import annotations

import os

import pygame

from src.config import DisplayConfig
from src.display.base import InputState


class PygameFbdevBackend:
    """Raspberry Pi backend that renders directly to the LCD framebuffer."""

    def __init__(
        self,
        config: DisplayConfig,
        fbdev: str = "/dev/fb0",
        title: str = "Aiqfome Eyes",
    ) -> None:
        os.environ.setdefault("SDL_VIDEODRIVER", "fbcon")
        os.environ.setdefault("SDL_FBDEV", fbdev)
        os.environ.setdefault("SDL_NOMOUSE", "1")

        pygame.init()
        pygame.mouse.set_visible(False)
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(
            (config.width, config.height),
            pygame.FULLSCREEN,
        )
        pygame.display.set_caption(title)
        self._running = True

    def get_surface(self) -> pygame.Surface:
        return self._screen

    def flip(self) -> None:
        pygame.display.flip()

    def tick(self, fps: int) -> None:
        self._clock.tick(fps)

    def handle_events(self) -> InputState:
        touches: list[tuple[int, int]] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._running = False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    touches.append(event.pos)
                else:
                    w, h = self._screen.get_size()
                    touches.append((int(event.x * w), int(event.y * h)))
        return InputState(running=self._running, touches=tuple(touches))

    def quit(self) -> None:
        pygame.quit()
