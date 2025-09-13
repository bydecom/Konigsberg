from __future__ import annotations

import pygame
from typing import Tuple, List, NamedTuple
from dataclasses import dataclass


@dataclass
class BridgeAnchor:
    """Điểm neo cầu trên mép vùng đất."""
    
    id: str  # ID duy nhất, ví dụ: "north_1", "kneiphof_3"
    x: float  # tọa độ x
    y: float  # tọa độ y
    region: str  # vùng đất: "north", "south", "kneiphof", "lomse"
    index: int  # thứ tự trong vùng (0-9)
    
    def get_rect(self, radius: int = 6) -> pygame.Rect:
        """Lấy hình chữ nhật bao quanh điểm neo để kiểm tra collision."""
        return pygame.Rect(
            self.x - radius,
            self.y - radius,
            radius * 2,
            radius * 2
        )
    
    def contains_point(self, point: Tuple[float, float], radius: int = 6) -> bool:
        """Kiểm tra xem điểm có nằm trong vùng neo không."""
        px, py = point
        distance_squared = (px - self.x) ** 2 + (py - self.y) ** 2
        return distance_squared <= radius ** 2


class BridgeAnchorManager:
    """Quản lý tất cả các điểm neo cầu trong bản đồ Königsberg."""
    
    def __init__(self) -> None:
        self.anchors: List[BridgeAnchor] = []
        
        # Màu sắc cho từng vùng
        self.region_colors = {
            "north": (255, 100, 100),    # đỏ nhạt
            "south": (100, 100, 255),    # xanh dương nhạt
            "kneiphof": (100, 255, 100), # xanh lá nhạt
            "lomse": (255, 255, 100),    # vàng nhạt
        }
        
    def generate_anchors(self, rect: pygame.Rect) -> None:
        """Tạo điểm neo cho các vùng đất: North (8), South (8), Kneiphof (11), Lomse (11) - tổng 38 điểm."""
        self.anchors.clear()
        
        # Vùng phía bắc - 8 điểm dọc theo mép dưới
        self._create_north_anchors(rect)
        
        # Vùng phía nam - 8 điểm dọc theo mép trên
        self._create_south_anchors(rect)
        
        # Đảo Kneiphof - 11 điểm xung quanh
        self._create_kneiphof_anchors(rect)
        
        # Đảo Lomse - 11 điểm xung quanh
        self._create_lomse_anchors(rect)
    
    def _create_north_anchors(self, rect: pygame.Rect) -> None:
        """Tạo 8 điểm neo cho vùng phía bắc: 4 điểm trái (thiên về Kneiphof), 4 điểm phải (thiên về Lomse)."""
        y = rect.y + rect.height * 0.25  # dịch lên gần mép hơn (từ 0.28 về 0.25)
        
        # 4 điểm bên trái thiên về đảo Kneiphof - thưa ra hơn (x = 0.28 đến 0.44)
        left_start = rect.x + rect.width * 0.28  # dịch về mép trái hơn
        left_end = rect.x + rect.width * 0.44    # mở rộng khoảng cách
        for i in range(4):
            x = left_start + (left_end - left_start) * i / 3
            anchor = BridgeAnchor(
                id=f"north_{i}",
                x=x,
                y=y,
                region="north",
                index=i
            )
            self.anchors.append(anchor)
        
        # 4 điểm bên phải thiên về đảo Lomse - dịch sang phải hơn (x = 0.66 đến 0.82)
        right_start = rect.x + rect.width * 0.66  # dịch sang phải hơn
        right_end = rect.x + rect.width * 0.82    # dịch về mép phải hơn nữa
        for i in range(4):
            x = right_start + (right_end - right_start) * i / 3
            anchor = BridgeAnchor(
                id=f"north_{4 + i}",
                x=x,
                y=y,
                region="north",
                index=4 + i
            )
            self.anchors.append(anchor)
    
    def _create_south_anchors(self, rect: pygame.Rect) -> None:
        """Tạo 8 điểm neo cho vùng phía nam: 4 điểm trái (thiên về Kneiphof), 4 điểm phải (thiên về Lomse)."""
        y = rect.y + rect.height * 0.75  # dịch xuống gần mép hơn (từ 0.72 về 0.75)
        
        # 4 điểm bên trái thiên về đảo Kneiphof - thưa ra hơn (x = 0.28 đến 0.44)
        left_start = rect.x + rect.width * 0.28  # dịch về mép trái hơn
        left_end = rect.x + rect.width * 0.44    # mở rộng khoảng cách
        for i in range(4):
            x = left_start + (left_end - left_start) * i / 3
            anchor = BridgeAnchor(
                id=f"south_{i}",
                x=x,
                y=y,
                region="south",
                index=i
            )
            self.anchors.append(anchor)
        
        # 4 điểm bên phải thiên về đảo Lomse - dịch sang phải hơn (x = 0.66 đến 0.82)
        right_start = rect.x + rect.width * 0.66  # dịch sang phải hơn
        right_end = rect.x + rect.width * 0.82    # dịch về mép phải hơn nữa
        for i in range(4):
            x = right_start + (right_end - right_start) * i / 3
            anchor = BridgeAnchor(
                id=f"south_{4 + i}",
                x=x,
                y=y,
                region="south",
                index=4 + i
            )
            self.anchors.append(anchor)
    
    def _create_kneiphof_anchors(self, rect: pygame.Rect) -> None:
        """Tạo 11 điểm neo cho đảo Kneiphof: 4 điểm trên, 4 điểm dưới, 3 điểm phải (về phía Lomse)."""
        center_x = rect.x + rect.width * 0.35
        center_y = rect.y + rect.height * 0.5
        width = rect.width * 0.35
        height = rect.height * 0.35
        
        import math
        
        # 4 điểm lệch trên (từ góc 70° đến 110°)
        for i in range(4):
            angle = math.radians(70 + i * 13.33)  # từ 70° đến 110°
            x = center_x + (width / 2) * 0.9 * math.cos(angle)
            y = center_y + (height / 2) * 0.9 * math.sin(angle)
            
            anchor = BridgeAnchor(
                id=f"kneiphof_{i}",
                x=x,
                y=y,
                region="kneiphof",
                index=i
            )
            self.anchors.append(anchor)
        
        # 4 điểm lệch dưới (từ góc 250° đến 290°)
        for i in range(4):
            angle = math.radians(250 + i * 13.33)  # từ 250° đến 290°
            x = center_x + (width / 2) * 0.9 * math.cos(angle)
            y = center_y + (height / 2) * 0.9 * math.sin(angle)
            
            anchor = BridgeAnchor(
                id=f"kneiphof_{4 + i}",
                x=x,
                y=y,
                region="kneiphof",
                index=4 + i
            )
            self.anchors.append(anchor)
        
        # 3 điểm lệch về phía đảo Lomse (từ góc -20° đến 20°)
        for i in range(3):
            angle = math.radians(-20 + i * 20)  # từ -20° đến 20°
            x = center_x + (width / 2) * 0.9 * math.cos(angle)
            y = center_y + (height / 2) * 0.9 * math.sin(angle)
            
            anchor = BridgeAnchor(
                id=f"kneiphof_{8 + i}",
                x=x,
                y=y,
                region="kneiphof",
                index=8 + i
            )
            self.anchors.append(anchor)
    
    def _create_lomse_anchors(self, rect: pygame.Rect) -> None:
        """Tạo 11 điểm neo cho đảo Lomse: 4 điểm trên, 4 điểm dưới, 3 điểm trái (về phía Kneiphof)."""
        center_x = rect.x + rect.width * 0.75
        center_y = rect.y + rect.height * 0.5
        width = rect.width * 0.35
        height = rect.height * 0.35
        
        import math
        
        # 4 điểm lệch trên (từ góc 70° đến 110°)
        for i in range(4):
            angle = math.radians(70 + i * 13.33)  # từ 70° đến 110°
            x = center_x + (width / 2) * 0.9 * math.cos(angle)
            y = center_y + (height / 2) * 0.9 * math.sin(angle)
            
            anchor = BridgeAnchor(
                id=f"lomse_{i}",
                x=x,
                y=y,
                region="lomse",
                index=i
            )
            self.anchors.append(anchor)
        
        # 4 điểm lệch dưới (từ góc 250° đến 290°)
        for i in range(4):
            angle = math.radians(250 + i * 13.33)  # từ 250° đến 290°
            x = center_x + (width / 2) * 0.9 * math.cos(angle)
            y = center_y + (height / 2) * 0.9 * math.sin(angle)
            
            anchor = BridgeAnchor(
                id=f"lomse_{4 + i}",
                x=x,
                y=y,
                region="lomse",
                index=4 + i
            )
            self.anchors.append(anchor)
        
        # 3 điểm lệch về phía đảo Kneiphof (từ góc 160° đến 200°)
        for i in range(3):
            angle = math.radians(160 + i * 20)  # từ 160° đến 200°
            x = center_x + (width / 2) * 0.9 * math.cos(angle)
            y = center_y + (height / 2) * 0.9 * math.sin(angle)
            
            anchor = BridgeAnchor(
                id=f"lomse_{8 + i}",
                x=x,
                y=y,
                region="lomse",
                index=8 + i
            )
            self.anchors.append(anchor)
    
    def draw_anchors(self, surface: pygame.Surface, highlighted_anchors: list = None) -> None:
        """Vẽ tất cả các điểm neo lên surface."""
        if highlighted_anchors is None:
            highlighted_anchors = []
            
        # Khởi tạo font để vẽ tên điểm
        if not hasattr(self, 'font'):
            try:
                self.font = pygame.font.SysFont("arial", 10)
            except:
                self.font = pygame.font.Font(None, 12)
            
        for anchor in self.anchors:
            color = self.region_colors.get(anchor.region, (128, 128, 128))
            
            # Kiểm tra xem anchor có được highlight không
            is_highlighted = anchor in highlighted_anchors
            radius = 8 if is_highlighted else 5  # To ra khi được highlight
            border_width = 3 if is_highlighted else 2
            
            # Vẽ điểm neo như hình tròn nhỏ
            pygame.draw.circle(surface, color, (int(anchor.x), int(anchor.y)), radius)
            
            # Vẽ viền đen (hoặc vàng nếu highlighted)
            border_color = (255, 215, 0) if is_highlighted else (0, 0, 0)  # Vàng khi highlight
            pygame.draw.circle(surface, border_color, (int(anchor.x), int(anchor.y)), radius, border_width)
            
    
    def get_anchor_by_id(self, anchor_id: str) -> BridgeAnchor | None:
        """Lấy điểm neo theo ID."""
        for anchor in self.anchors:
            if anchor.id == anchor_id:
                return anchor
        return None
    
    def get_anchor_at_point(self, point: Tuple[float, float]) -> BridgeAnchor | None:
        """Lấy điểm neo tại vị trí được click."""
        for anchor in self.anchors:
            if anchor.contains_point(point):
                return anchor
        return None
    
    def get_anchors_by_region(self, region: str) -> List[BridgeAnchor]:
        """Lấy tất cả điểm neo của một vùng."""
        return [anchor for anchor in self.anchors if anchor.region == region]
