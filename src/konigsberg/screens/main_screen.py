from __future__ import annotations

import pygame
from typing import Tuple

from .base import Screen
from .sub_screen import SubScreen


class MainScreen(Screen):
    """Màn hình chính, chứa một màn hình phụ nằm bên trong."""

    def __init__(self, app) -> None:
        self.app = app
        self.background_color: Tuple[int, int, int] = (245, 245, 245)
        self.border_color: Tuple[int, int, int] = (0, 0, 0)
        self.text_color: Tuple[int, int, int] = (0, 0, 0)
        self.sub_screen = SubScreen(self)
        
        # Khởi tạo font hỗ trợ tiếng Việt
        try:
            # Thử sử dụng font hệ thống hỗ trợ Unicode
            self.font = pygame.font.SysFont("segoeui", 20)  # Segoe UI hỗ trợ tiếng Việt tốt
        except:
            try:
                self.font = pygame.font.SysFont("arial", 20)  # Arial fallback
            except:
                self.font = pygame.font.Font(None, 20)  # Font mặc định

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Cho phép thoát nhanh bằng phím ESC
            self.app.running = False
        
        # Chuyển các sự kiện chuột vào SubScreen
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.sub_screen.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.sub_screen.handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.sub_screen.handle_mouse_motion(event.pos)

    def update(self, dt_ms: int) -> None:  # noqa: ARG002 - chưa cần dùng dt_ms
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.background_color)

        # Vẽ khung ngoài (màn hình chính)
        outer_margin = 12
        outer_rect = pygame.Rect(
            outer_margin,
            outer_margin,
            self.app.width - 2 * outer_margin,
            self.app.height - 2 * outer_margin,
        )
        pygame.draw.rect(surface, self.border_color, outer_rect, 2)

        # Tính toán vùng màn hình phụ lệch trái, giống minh họa
        inner_gap = 24
        sub_left = outer_rect.left + inner_gap
        sub_top = outer_rect.top + inner_gap
        sub_width = int(self.app.width * 0.7) - inner_gap - outer_margin
        sub_height = self.app.height - 2 * (outer_margin + inner_gap)
        sub_rect = pygame.Rect(sub_left, sub_top, sub_width, sub_height)

        # Vẽ SubScreen
        self.sub_screen.draw(surface, sub_rect)
        
        # Tính toán vùng văn bản phân tích (phần còn trống bên phải)
        analysis_left = sub_rect.right + inner_gap
        analysis_top = sub_rect.top
        analysis_width = outer_rect.right - analysis_left - inner_gap
        analysis_height = sub_rect.height
        analysis_rect = pygame.Rect(analysis_left, analysis_top, analysis_width, analysis_height)
        
        # Vẽ văn bản phân tích trong vùng còn trống
        self._draw_analysis_text(surface, analysis_rect)
    
    def _draw_analysis_text(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Vẽ văn bản phân tích trong vùng được chỉ định."""
        # Lấy kết quả phân tích từ SubScreen
        analysis_result = self.sub_screen.get_analysis_result()
        
        if not analysis_result:
            return
            
        # Vẽ khung cho vùng phân tích
        pygame.draw.rect(surface, (255, 255, 255), rect)  # Nền trắng
        pygame.draw.rect(surface, self.border_color, rect, 2)  # Viền đen
        
        # Vẽ tiêu đề
        title = "KẾT QUẢ PHÂN TÍCH"
        title_surface = self.font.render(title, True, self.text_color)
        title_rect = title_surface.get_rect(centerx=rect.centerx, y=rect.y + 20)
        surface.blit(title_surface, title_rect)
        
        # Vẽ đường gạch dưới tiêu đề
        line_y = title_rect.bottom + 10
        pygame.draw.line(surface, self.border_color, 
                        (rect.x + 20, line_y), 
                        (rect.right - 20, line_y), 2)
        
        # Vẽ nội dung phân tích
        start_y = line_y + 20
        line_height = 28
        
        for i, line in enumerate(analysis_result):
            if start_y + i * line_height > rect.bottom - 20:  # Kiểm tra không vượt quá khung
                break
                
            text_surface = self.font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(x=rect.x + 20, y=start_y + i * line_height)
            surface.blit(text_surface, text_rect)


