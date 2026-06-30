from __future__ import annotations

import pygame

from src.config import DisplayConfig
from src.display.base import InputState


class PygameWindowBackend:
    """Desktop backend — janela normal ou fullscreen sem bordas."""

    def __init__(
        self,
        config: DisplayConfig,
        title: str = "Aiqfome Eyes",
        fullscreen: bool | None = None,
    ) -> None:
        pygame.init()
        self._clock = pygame.time.Clock()
        self._fullscreen = config.fullscreen if fullscreen is None else fullscreen

        if self._fullscreen:
            flags = pygame.FULLSCREEN
            pygame.mouse.set_visible(False)
        else:
            flags = pygame.RESIZABLE

        self._screen = pygame.display.set_mode((config.width, config.height), flags)

        if not self._fullscreen:
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
