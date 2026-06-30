from __future__ import annotations

import os


class PygameFbdevBackend:
    """Raspberry Pi backend that renders directly to the LCD framebuffer."""

    def __init__(self, config, fbdev="/dev/fb0", title="Aiqfome Eyes"):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_NOMOUSE"] = "1"

        import pygame

        self._pygame = pygame
        self._fbdev_path = fbdev
        self._config = config
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode((config.width, config.height))
        self._running = True

    def get_surface(self):
        return self._screen

    def flip(self):
        pygame = self._pygame
        pygame.display.flip()

        try:
            fb_surface = self._screen.convert(16)
            raw_data = pygame.image.tostring(fb_surface, "RGB565")
            with open(self._fbdev_path, "wb") as fb:
                fb.write(raw_data)
        except OSError:
            pass

    def tick(self, fps):
        self._clock.tick(fps)

    def handle_events(self):
        from src.display.base import InputState

        pygame = self._pygame
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
        self._pygame.quit()
