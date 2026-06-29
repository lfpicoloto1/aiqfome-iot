from __future__ import annotations

import pygame


def draw_eyes(
    surface: pygame.Surface,
    center_x: int,
    center_y: int,
    eye_width: int,
    eye_height: int,
    gap: int,
    color: tuple[int, int, int],
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
) -> None:
    """Draw a pair of vertical oval eyes with logo-fixed gap between them."""
    scaled_width = max(int(eye_width * scale_x), 2)
    scaled_height = max(int(eye_height * scale_y), 2)
    half_gap = gap // 2
    left_cx = center_x - half_gap - eye_width // 2 + int(offset_x)
    right_cx = center_x + half_gap + eye_width // 2 + int(offset_x)
    draw_y = center_y + int(offset_y)

    for cx in (left_cx, right_cx):
        rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        rect.center = (cx, draw_y)
        pygame.draw.ellipse(surface, color, rect)
