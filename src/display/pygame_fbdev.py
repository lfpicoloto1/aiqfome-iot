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
        fbdev: str = "/dev/fb1",  # Mudamos o padrão para fb1 por segurança
        title: str = "Aiqfome Eyes",
    ) -> None:
        # Força o Pygame a rodar na memória (sem depender de drivers X11 ou fbdev nativos)
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_NOMOUSE"] = "1"
        
        pygame.init()
        
        # Guardamos o caminho da tela pequena para usar depois
        self._fbdev_path = fbdev 
        self._config = config
        self._clock = pygame.time.Clock()
        
        # Cria a tela na memória com a resolução correta
        self._screen = pygame.display.set_mode(
            (config.width, config.height)
        )
        self._running = True

    def get_surface(self) -> pygame.Surface:
        return self._screen

    def flip(self) -> None:
            # 1. Faz o Pygame atualizar a surface interna
        pygame.display.flip()
            
            # 2. Copia os pixels da memória direto para o hardware da telinha (/dev/fb1)
        try:
                # Transforma os gráficos do pygame em bytes puros de imagem (RGB ou RGBA)
            raw_data = pygame.image.tostring(self._screen, "RGB")
                
                # Abre o arquivo da tela pequena e escreve os pixels brutos lá dentro
            with open(self._fbdev_path, "wb") as fb:
                    fb.write(raw_data)
        except Exception as e:
                # Evita crashar o loop se houver erro temporário de escrita
            pass

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
