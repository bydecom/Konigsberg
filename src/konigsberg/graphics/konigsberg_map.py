from __future__ import annotations

import pygame
from typing import Tuple, List
from .bridge_anchor import BridgeAnchorManager


class KonigsbergMap:
    """Vẽ bản đồ Königsberg với 4 vùng đất và dòng sông."""
    
    def __init__(self) -> None:
        # Màu sắc
        self.water_color: Tuple[int, int, int] = (173, 216, 230)  # xanh nước nhạt
        self.land_color: Tuple[int, int, int] = (144, 238, 144)   # xanh lá nhạt
        self.land_border: Tuple[int, int, int] = (34, 139, 34)    # xanh lá đậm
        
        # Quản lý điểm neo cầu
        self.anchor_manager = BridgeAnchorManager()
        
        # Khởi tạo font cho số vùng đất
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)  # Sử dụng font mặc định, kích thước 36

    def draw(self, surface: pygame.Surface, rect: pygame.Rect, highlighted_anchors: list = None) -> None:
        """Vẽ bản đồ Königsberg trong vùng rect cho trước."""
        # Làm sạch nền với màu nước
        pygame.draw.rect(surface, self.water_color, rect)
        
        # Tính toán tỉ lệ và vị trí
        width, height = rect.width, rect.height
        center_x = rect.x + width // 2
        center_y = rect.y + height // 2
        
        # Vẽ 4 vùng đất theo layout Königsberg
        self._draw_north_bank(surface, rect)  # Vùng phía bắc (trên)
        self._draw_south_bank(surface, rect)  # Vùng phía nam (dưới) 
        self._draw_kneiphof_island(surface, rect)  # Đảo Kneiphof (giữa)
        self._draw_lomse_island(surface, rect)  # Đảo Lomse (nhỏ, dưới giữa)
        
        # Tạo và vẽ các điểm neo cầu
        self.anchor_manager.generate_anchors(rect)
        self.anchor_manager.draw_anchors(surface, highlighted_anchors)
        
        # Vẽ số trên các vùng đất
        self._draw_land_numbers(surface, rect)

    def _draw_north_bank(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Vẽ bờ phía bắc (vùng đất trên) - sát rìa trên và hai bên, giảm chiều rộng."""
        points = [
            (rect.x, rect.y),  # góc trên trái
            (rect.x + rect.width, rect.y),  # góc trên phải
            (rect.x + rect.width, rect.y + rect.height * 0.25),  # phải xuống (giảm từ 0.35 xuống 0.25)
            (rect.x + rect.width * 0.7, rect.y + rect.height * 0.28),  # cắt vào trong (giảm từ 0.75 xuống 0.7)
            (rect.x + rect.width * 0.3, rect.y + rect.height * 0.28),  # cắt vào trong (tăng từ 0.25 lên 0.3)
            (rect.x, rect.y + rect.height * 0.25),  # trái xuống (giảm từ 0.35 xuống 0.25)
        ]
        pygame.draw.polygon(surface, self.land_color, points)
        pygame.draw.polygon(surface, self.land_border, points, 2)
        
    def _draw_south_bank(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Vẽ bờ phía nam (vùng đất dưới) - sát rìa dưới và hai bên, giảm chiều rộng."""
        points = [
            (rect.x, rect.y + rect.height * 0.75),  # trái lên (tăng từ 0.65 lên 0.75)
            (rect.x + rect.width * 0.3, rect.y + rect.height * 0.72),  # cắt vào trong (tăng từ 0.25 lên 0.3)
            (rect.x + rect.width * 0.7, rect.y + rect.height * 0.72),  # cắt vào trong (giảm từ 0.75 xuống 0.7)
            (rect.x + rect.width, rect.y + rect.height * 0.75),  # phải lên (tăng từ 0.65 lên 0.75)
            (rect.x + rect.width, rect.y + rect.height),  # góc dưới phải
            (rect.x, rect.y + rect.height),  # góc dưới trái
        ]
        pygame.draw.polygon(surface, self.land_color, points)
        pygame.draw.polygon(surface, self.land_border, points, 2)
        
    def _draw_kneiphof_island(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Vẽ đảo Kneiphof (đảo lớn ở giữa trái) - tăng kích thước và dịch sang trái."""
        center_x = rect.x + rect.width * 0.35  # dịch từ 0.5 sang 0.4 (về phía trái)
        center_y = rect.y + rect.height * 0.5
        width = rect.width * 0.35  # tăng từ 0.25 lên 0.3
        height = rect.height * 0.35  # tăng từ 0.16 lên 0.18
        
        island_rect = pygame.Rect(
            center_x - width // 2,
            center_y - height // 2,
            width,
            height
        )
        pygame.draw.ellipse(surface, self.land_color, island_rect)
        pygame.draw.ellipse(surface, self.land_border, island_rect, 2)
        
    def _draw_lomse_island(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Vẽ đảo Lomse (đảo lớn phía phải) - tăng kích thước và dịch sang phải."""
        center_x = rect.x + rect.width * 0.75  # dịch từ 0.72 sang 0.75 (về phía phải hơn)
        center_y = rect.y + rect.height * 0.5   # đưa lên giữa từ 0.55
        width = rect.width * 0.35  # tăng từ 0.22 lên 0.28
        height = rect.height * 0.35  # tăng từ 0.12 lên 0.16
        
        island_rect = pygame.Rect(
            center_x - width // 2,
            center_y - height // 2, 
            width,
            height
        )
        pygame.draw.ellipse(surface, self.land_color, island_rect)
        pygame.draw.ellipse(surface, self.land_border, island_rect, 2)

    def _draw_land_numbers(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Vẽ số 1, 2, 3, 4 lên các vùng đất."""
        text_color = (0, 0, 0) # Màu đen

        # Vùng 1: Bờ phía bắc
        text_surface_1 = self.font.render("1", True, text_color)
        text_rect_1 = text_surface_1.get_rect(center=(rect.x + rect.width * 0.5, rect.y + rect.height * 0.15))
        surface.blit(text_surface_1, text_rect_1)

        # Vùng 2: Đảo Kneiphof (tính toán lại tâm từ _draw_kneiphof_island)
        center_x_kneiphof = rect.x + rect.width * 0.35
        center_y_kneiphof = rect.y + rect.height * 0.5
        text_surface_2 = self.font.render("2", True, text_color)
        text_rect_2 = text_surface_2.get_rect(center=(center_x_kneiphof, center_y_kneiphof))
        surface.blit(text_surface_2, text_rect_2)

        # Vùng 3: Đảo Lomse (tính toán lại tâm từ _draw_lomse_island)
        center_x_lomse = rect.x + rect.width * 0.75
        center_y_lomse = rect.y + rect.height * 0.5
        text_surface_3 = self.font.render("3", True, text_color)
        text_rect_3 = text_surface_3.get_rect(center=(center_x_lomse, center_y_lomse))
        surface.blit(text_surface_3, text_rect_3)

        # Vùng 4: Bờ phía nam
        text_surface_4 = self.font.render("4", True, text_color)
        text_rect_4 = text_surface_4.get_rect(center=(rect.x + rect.width * 0.5, rect.y + rect.height * 0.88))
        surface.blit(text_surface_4, text_rect_4)
