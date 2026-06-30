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
            # 1. Criamos uma cópia da superfície convertendo explicitamente para 16 bits (RGB565)
            # Isso é o formato nativo perfeito que a Waveshare precisa!
            fb_surface = self._screen.convert(16)
            
            # 2. Extraímos a string de bytes puros nesse formato de 16 bits
            raw_data = pygame.image.tostring(fb_surface, "RGB565")
            
            # 3. Injetamos os bytes perfeitamente alinhados no arquivo de hardware
            with open(self._fbdev_path, "wb") as fb:
                fb.write(raw_data)
        except Exception as e:
            # Evita travar o projeto se houver alguma oscilação de escrita no arquivo
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
