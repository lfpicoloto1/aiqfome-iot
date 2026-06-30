from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_NOMOUSE", "1")

import pygame

from src.config import DisplayConfig
from src.display.base import InputState


class PygameFbdevBackend:
    """Raspberry Pi backend that renders directly to the LCD framebuffer."""

    def __init__(self, config, fbdev="/dev/fb0", title="Aiqfome Eyes"):
        self._fbdev_path = fbdev
        self._config = config
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode((config.width, config.height))
        self._running = True

    def get_surface(self):
        return self._screen

    def flip(self):
        pygame.display.flip()
        try:
            raw_data = pygame.image.tostring(self._screen, "RGB")
            with open(self._fbdev_path, "wb") as fb:
                fb.write(raw_data)
        except OSError:
            pass

    def tick(self, fps):
        self._clock.tick(fps)

    def handle_events(self):
        touches = []
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

    def quit(self):
        pygame.quit()
