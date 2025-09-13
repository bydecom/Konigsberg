from __future__ import annotations

import pygame
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class GraphNode:
    """Đỉnh của đồ thị Königsberg."""
    
    id: str  # ID của node: "1", "2", "3", "4"
    x: float  # tọa độ x
    y: float  # tọa độ y 
    label: str  # nhãn hiển thị
    radius: int = 25  # bán kính
    
    def get_rect(self) -> pygame.Rect:
        """Lấy hình chữ nhật bao quanh node để kiểm tra collision."""
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """Kiểm tra xem điểm có nằm trong node không."""
        px, py = point
        distance_squared = (px - self.x) ** 2 + (py - self.y) ** 2
        return distance_squared <= self.radius ** 2


class GraphNodeManager:
    """Quản lý 4 đỉnh đồ thị Königsberg ở panel bên phải."""
    
    def __init__(self) -> None:
        self.nodes: List[GraphNode] = []
        
        # Màu sắc
        self.node_color = (255, 255, 255)  # trắng
        self.node_border = (0, 0, 0)  # đen
        self.text_color = (0, 0, 0)  # đen
        self.selected_color = (255, 200, 200)  # đỏ nhạt khi được chọn
        
        self.font = None  # sẽ được khởi tạo khi cần
        self.selected_node: GraphNode | None = None
        
    def generate_nodes(self, panel_rect: pygame.Rect) -> None:
        """Tạo 4 node trong vùng panel bên phải."""
        self.nodes.clear()
        
        # Tạo font nếu chưa có
        if self.font is None:
            self.font = pygame.font.Font(None, 36)
        
        # Tính toán vị trí 4 node theo layout: 1 trên, 2-3 giữa, 4 dưới
        center_x = panel_rect.x + panel_rect.width // 2
        center_y = panel_rect.y + panel_rect.height // 2
        
        offset_x = 80  # khoảng cách ngang giữa node 2 và 3 (tăng từ 50)
        offset_y = 80  # khoảng cách dọc (tăng từ 55)
        
        # Vị trí các node theo layout mới
        positions = [
            (center_x, center_y - offset_y),        # Node 1 - ở trên (giữa)
            (center_x - offset_x, center_y),        # Node 2 - ở giữa trái
            (center_x + offset_x, center_y),        # Node 3 - ở giữa phải
            (center_x, center_y + offset_y),        # Node 4 - ở dưới (giữa)
        ]
        
        # Tạo 4 node tương ứng với 4 vùng đất
        labels = ["1", "2", "3", "4"]  # 1=Bắc, 2=Kneiphof, 3=Nam, 4=Lomse
        
        for i, (x, y) in enumerate(positions):
            node = GraphNode(
                id=str(i + 1),
                x=x,
                y=y,
                label=labels[i]
            )
            self.nodes.append(node)
    
    def draw_nodes(self, surface: pygame.Surface) -> None:
        """Vẽ tất cả các node lên surface."""
        for node in self.nodes:
            # Chọn màu node
            fill_color = self.selected_color if node == self.selected_node else self.node_color
            
            # Vẽ node (hình tròn)
            pygame.draw.circle(surface, fill_color, (int(node.x), int(node.y)), node.radius)
            pygame.draw.circle(surface, self.node_border, (int(node.x), int(node.y)), node.radius, 3)
            
            # Vẽ label
            if self.font:
                text_surface = self.font.render(node.label, True, self.text_color)
                text_rect = text_surface.get_rect(center=(int(node.x), int(node.y)))
                surface.blit(text_surface, text_rect)
    
    def handle_click(self, point: Tuple[float, float]) -> GraphNode | None:
        """Xử lý click vào node và trả về node được click."""
        for node in self.nodes:
            if node.contains_point(point):
                self.selected_node = node
                return node
        return None
    
    def get_node_by_id(self, node_id: str) -> GraphNode | None:
        """Lấy node theo ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def clear_selection(self) -> None:
        """Bỏ chọn tất cả node."""
        self.selected_node = None
