from __future__ import annotations

import pygame


class Screen:
    """Giao diện tối giản cho một màn hình vẽ trong ứng dụng Pygame."""

    def handle_event(self, event: pygame.event.Event) -> None:  # noqa: D401 - mô tả đơn giản
        """Xử lý sự kiện bàn phím/chuột."""

    def update(self, dt_ms: int) -> None:  # noqa: D401
        """Cập nhật trạng thái theo thời gian (milliseconds)."""

    def draw(self, surface: pygame.Surface) -> None:  # noqa: D401
        """Vẽ nội dung của màn hình lên surface đích."""


