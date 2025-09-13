from __future__ import annotations

import pygame
from typing import Optional

from .screens.main_screen import MainScreen
from .screens.base import Screen


class App:
    """Lớp ứng dụng chịu trách nhiệm khởi tạo, vòng lặp game và giải phóng tài nguyên.

    Sử dụng như một context manager để đảm bảo `pygame.quit()` luôn được gọi.
    """

    def __init__(self, width: int = 1540, height: int = 800, title: str = "Königsberg - Graph UI") -> None:
        self.width = width
        self.height = height
        self.title = title

        self.screen_surface: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.active_screen: Optional[Screen] = None
        self.running: bool = False

    # --- Resource management -------------------------------------------------
    def __enter__(self) -> "App":
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen_surface = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # Màn hình chính
        self.active_screen = MainScreen(self)
        self.running = True
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001 - theo ngữ cảnh context manager
        try:
            self.active_screen = None
        finally:
            pygame.quit()

    # --- Main loop -----------------------------------------------------------
    def run(self) -> None:
        assert self.screen_surface is not None, "App chưa được khởi tạo đúng cách"
        assert self.clock is not None, "Clock chưa được khởi tạo"

        while self.running:
            dt_ms = self.clock.tick(60)  # giới hạn 60 FPS và lấy delta time (ms)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.active_screen is not None:
                    self.active_screen.handle_event(event)

            if self.active_screen is not None:
                self.active_screen.update(dt_ms)
                self.active_screen.draw(self.screen_surface)

            pygame.display.flip()


