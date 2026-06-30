from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.animation.animator import EyeAnimator
from src.animation.eyes import draw_eyes
from src.config import AppConfig, hex_to_rgb, load_config


def _default_config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config.yaml"


def _create_backend(name: str, config: AppConfig, fbdev: str, fullscreen: bool | None):
    if name == "window":
        from src.display.pygame_window import PygameWindowBackend

        return PygameWindowBackend(config.display, fullscreen=fullscreen)
    if name == "fbdev":
        from src.display.pygame_fbdev import PygameFbdevBackend

        return PygameFbdevBackend(config.display, fbdev=fbdev)
    raise ValueError(f"Unknown backend: {name}")


def run(config_path: Path, backend_name: str, fbdev: str, fullscreen: bool | None) -> int:
    config = load_config(config_path)
    backend = _create_backend(backend_name, config, fbdev, fullscreen)
    animator = EyeAnimator(config)

    bg_color = hex_to_rgb(config.colors.background)
    center_x = config.display.width // 2

    try:
        running = True
        while running:
            input_state = backend.handle_events()
            running = input_state.running

            for touch_x, touch_y in input_state.touches:
                animator.on_touch(touch_x, touch_y)

            pose = animator.update()
            surface = backend.get_surface()
            surface.fill(bg_color)
            draw_eyes(
                surface=surface,
                center_x=center_x,
                center_y=config.eyes.center_y,
                eye_width=config.eyes.width,
                eye_height=config.eyes.height,
                gap=config.eyes.gap,
                color=pose.color,
                scale_x=pose.scale_x,
                scale_y=pose.scale_y,
                offset_x=pose.offset_x,
                offset_y=pose.offset_y,
            )
            backend.flip()
            backend.tick(config.display.fps)
    finally:
        backend.quit()

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aiqfome Eyes — animated ghost eyes")
    parser.add_argument(
        "--config",
        type=Path,
        default=_default_config_path(),
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--backend",
        choices=("window", "fbdev"),
        default="window",
        help="Display backend: window (dev) or fbdev (Raspberry Pi LCD)",
    )
    parser.add_argument(
        "--fbdev",
        default="/dev/fb0",
        help="Framebuffer device path (fbdev backend only)",
    )
    parser.add_argument(
        "--fullscreen",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Fullscreen sem bordas (window backend). Padrão: display.fullscreen no config",
    )
    args = parser.parse_args(argv)

    if not args.config.exists():
        print(f"Config not found: {args.config}", file=sys.stderr)
        return 1

    return run(args.config, args.backend, args.fbdev, args.fullscreen)


if __name__ == "__main__":
    raise SystemExit(main())
