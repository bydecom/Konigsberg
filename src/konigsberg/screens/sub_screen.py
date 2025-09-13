from __future__ import annotations

from typing import Tuple

import pygame
import networkx as nx

from ..graphics.konigsberg_map import KonigsbergMap
from ..graphics.graph_nodes import GraphNodeManager
from ..graphics.bridge_anchor import BridgeAnchor


class SubScreen:
    """Màn hình phụ hiển thị bản đồ Königsberg bên trái và đồ thị 4 đỉnh bên phải."""

    def __init__(self, main_screen) -> None:
        self.main_screen = main_screen
        self.border_color: Tuple[int, int, int] = (0, 0, 0)
        self.background_color: Tuple[int, int, int] = (255, 255, 255)
        self.panel_divider_color: Tuple[int, int, int] = (128, 128, 128)
        self.bridge_color: Tuple[int, int, int] = (139, 69, 19) # SaddleBrown
        self.text_color: Tuple[int, int, int] = (0, 0, 0)
        
        # Components
        self.konigsberg_map = KonigsbergMap()
        self.graph_nodes = GraphNodeManager()
        
        # Graph logic
        self.graph = nx.MultiGraph()  # Sử dụng MultiGraph để cho phép nhiều cạnh giữa 2 đỉnh
        self.bridges: list[tuple[BridgeAnchor, BridgeAnchor]] = []
        self.dragging = False
        self.start_anchor: BridgeAnchor | None = None
        self.mouse_pos = (0, 0)
        
        self.REGION_TO_NODE_ID = {
            "north": "1",
            "kneiphof": "2",
            "lomse": "3",
            "south": "4",
        }
        self.analysis_result: list[str] = []
        
        # Double click detection
        self.last_click_time = 0
        self.last_click_pos = (0, 0)
        self.double_click_threshold = 500  # milliseconds
        self.double_click_distance = 10  # pixels
        
        # Highlight system
        self.highlighted_anchors: list[BridgeAnchor] = []
        
        self._analyze_graph() # Initial analysis

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        # Vẽ nền và khung
        pygame.draw.rect(surface, self.background_color, rect)
        pygame.draw.rect(surface, self.border_color, rect, 3)
        
        # Chia SubScreen thành 2 phần: 70% bên trái cho map, 30% bên phải cho graph nodes
        inner_margin = 10
        inner_rect = pygame.Rect(
            rect.x + inner_margin,
            rect.y + inner_margin,
            rect.width - 2 * inner_margin,
            rect.height - 2 * inner_margin
        )
        
        # Vùng bản đồ (70% bên trái)
        map_width = int(inner_rect.width * 0.7)
        map_rect = pygame.Rect(
            inner_rect.x,
            inner_rect.y,
            map_width,
            inner_rect.height
        )
        
        # Vùng đồ thị (30% bên phải)
        graph_width = inner_rect.width - map_width
        graph_rect = pygame.Rect(
            inner_rect.x + map_width,
            inner_rect.y,
            graph_width,
            inner_rect.height
        )
        
        # Vẽ đường phân chia
        divider_x = inner_rect.x + map_width
        pygame.draw.line(
            surface, 
            self.panel_divider_color, 
            (divider_x, inner_rect.y), 
            (divider_x, inner_rect.y + inner_rect.height), 
            2
        )
        
        # Vẽ bản đồ Königsberg với highlighted anchors
        self.konigsberg_map.draw(surface, map_rect, self.highlighted_anchors)
        
        # Vẽ các cây cầu đã tạo
        for start, end in self.bridges:
            pygame.draw.line(surface, self.bridge_color, (start.x, start.y), (end.x, end.y), 5)
        
        # Vẽ đường nối khi đang kéo chuột
        if self.dragging and self.start_anchor:
            pygame.draw.line(surface, self.bridge_color, (self.start_anchor.x, self.start_anchor.y), self.mouse_pos, 4)
        
        # Vẽ 4 node đồ thị
        self.graph_nodes.generate_nodes(graph_rect)
        self.graph_nodes.draw_nodes(surface)
    
        # Vẽ các cạnh của đồ thị
        self._draw_graph_edges(surface)

    def handle_mouse_down(self, point: Tuple[float, float]) -> None:
        """Xử lý khi nhấn chuột trái."""
        current_time = pygame.time.get_ticks()
        
        # Kiểm tra double click
        time_diff = current_time - self.last_click_time
        pos_diff = ((point[0] - self.last_click_pos[0]) ** 2 + (point[1] - self.last_click_pos[1]) ** 2) ** 0.5
        
        if time_diff < self.double_click_threshold and pos_diff < self.double_click_distance:
            # Double click detected - try to remove bridge
            self._handle_bridge_removal(point)
        else:
            # Single click - start creating bridge and highlight valid targets
            anchor = self.konigsberg_map.anchor_manager.get_anchor_at_point(point)
            if anchor:
                self.dragging = True
                self.start_anchor = anchor
                self.mouse_pos = point
                # Highlight các điểm có thể kết nối
                self._highlight_valid_targets(anchor)
        
        # Update last click info
        self.last_click_time = current_time
        self.last_click_pos = point

    def handle_mouse_up(self, point: Tuple[float, float]) -> None:
        """Xử lý khi nhả chuột trái."""
        if self.dragging and self.start_anchor:
            end_anchor = self.konigsberg_map.anchor_manager.get_anchor_at_point(point)
            
            if end_anchor and self.start_anchor.region != end_anchor.region:
                # Kiểm tra xem có được phép kết nối không
                if self._is_valid_connection(self.start_anchor, end_anchor):
                    start_node = self.REGION_TO_NODE_ID[self.start_anchor.region]
                    end_node = self.REGION_TO_NODE_ID[end_anchor.region]

                    self.graph.add_edge(start_node, end_node)
                    self.bridges.append((self.start_anchor, end_anchor))
                    self._analyze_graph()

        self.dragging = False
        self.start_anchor = None
        # Clear highlights
        self.highlighted_anchors.clear()

    def handle_mouse_motion(self, point: Tuple[float, float]) -> None:
        """Xử lý khi di chuyển chuột."""
        if self.dragging:
            self.mouse_pos = point

    def _analyze_graph(self):
        """Phân tích đồ thị và cập nhật kết quả."""
        if not self.graph.nodes:
            self.graph.add_nodes_from(["1", "2", "3", "4"])
            
        degrees = dict(self.graph.degree())
        odd_degree_nodes = [node for node, degree in degrees.items() if degree % 2 != 0]
        total_edges = self.graph.number_of_edges()
        
        # Tìm các đỉnh có cạnh (bậc > 0)
        nodes_with_edges = [node for node, degree in degrees.items() if degree > 0]
        
        self.analysis_result = []
        
        # 1. Tính bậc của các đỉnh
        self.analysis_result.append("Bậc của các đỉnh:")
        for node in sorted(degrees.keys()):
             self.analysis_result.append(f"  - Đỉnh {node}: {degrees[node]}")
        self.analysis_result.append("") # Dòng trống

        # 2. Kiểm tra có cầu nào không
        if total_edges == 0:
            self.analysis_result.append("Kết luận: Chưa có cầu nào được xây dựng.")
            self.analysis_result.append("Hãy kéo thả giữa các vùng đất để tạo cầu!")
            return

        # 3. Kiểm tra tính liên thông của đồ thị con chứa các đỉnh có cạnh
        if len(nodes_with_edges) > 1:
            subgraph = self.graph.subgraph(nodes_with_edges)
            is_connected = nx.is_connected(subgraph)
        else:
            is_connected = True  # Nếu chỉ có 1 đỉnh có cạnh thì coi như liên thông

        # 4. Kiểm tra có đỉnh cô lập không
        isolated_nodes = [node for node, degree in degrees.items() if degree == 0]
        has_isolated_nodes = len(isolated_nodes) > 0

        # 5. Áp dụng định lý Euler
        if not is_connected or has_isolated_nodes:
            self.analysis_result.append("Kết luận: Không tồn tại Đường đi")
            self.analysis_result.append("hay Chu trình Euler.")
            if not is_connected:
                self.analysis_result.append("Lý do: Đồ thị không liên thông.")
            if has_isolated_nodes:
                self.analysis_result.append(f"Các đỉnh bị cô lập: {', '.join(sorted(isolated_nodes))}.")
        elif len(odd_degree_nodes) == 0:
            self.analysis_result.append("Kết luận: Tồn tại Chu trình Euler.")
            # Tìm chu trình Euler
            try:
                euler_circuit = list(nx.eulerian_circuit(self.graph))
                self.analysis_result.append("Chu trình Euler:")
                path_str = " → ".join([str(edge[0]) for edge in euler_circuit] + [str(euler_circuit[0][0])])
                # Chia đường đi thành nhiều dòng nếu quá dài
                if len(path_str) > 30:
                    words = path_str.split(" → ")
                    line = ""
                    for i, word in enumerate(words):
                        if len(line + word) > 30 and line:
                            self.analysis_result.append(f"  {line}")
                            line = word
                        else:
                            line += (" → " if line else "") + word
                    if line:
                        self.analysis_result.append(f"  {line}")
                else:
                    self.analysis_result.append(f"  {path_str}")
            except:
                self.analysis_result.append("(Có thể đi qua tất cả các cầu mỗi cầu một lần)")
                self.analysis_result.append("và quay về điểm xuất phát.")
        elif len(odd_degree_nodes) == 2:
            self.analysis_result.append("Kết luận: Chỉ tồn tại Đường đi Euler.")
            # Tìm đường đi Euler
            try:
                euler_path = list(nx.eulerian_path(self.graph))
                self.analysis_result.append("Đường đi Euler:")
                path_str = " → ".join([str(edge[0]) for edge in euler_path] + [str(euler_path[-1][1])])
                # Chia đường đi thành nhiều dòng nếu quá dài
                if len(path_str) > 30:
                    words = path_str.split(" → ")
                    line = ""
                    for i, word in enumerate(words):
                        if len(line + word) > 30 and line:
                            self.analysis_result.append(f"  {line}")
                            line = word
                        else:
                            line += (" → " if line else "") + word
                    if line:
                        self.analysis_result.append(f"  {line}")
                else:
                    self.analysis_result.append(f"  {path_str}")
            except:
                self.analysis_result.append("Phải bắt đầu ở một đỉnh bậc lẻ và")
                self.analysis_result.append(f"kết thúc ở đỉnh còn lại: {odd_degree_nodes[0]}, {odd_degree_nodes[1]}.")
        else:
            self.analysis_result.append("Kết luận: Không tồn tại Đường đi")
            self.analysis_result.append("hay Chu trình Euler.")
            self.analysis_result.append(f"Số đỉnh bậc lẻ là {len(odd_degree_nodes)}: {', '.join(sorted(odd_degree_nodes))}.")
            
    def _draw_graph_edges(self, surface: pygame.Surface) -> None:
        """Vẽ các cạnh (đường nối) giữa các node của đồ thị, nối từ rìa node, xử lý multi-edge bằng đường cong."""
        drawn_pairs = set()
        spacing = 8.0  # Khoảng cách giữa các đường cong

        for u, v in self.graph.edges():
            # Sắp xếp để xử lý mỗi cặp đỉnh một lần duy nhất
            u_node, v_node = tuple(sorted((u, v)))
            
            if (u_node, v_node) in drawn_pairs:
                continue
            drawn_pairs.add((u_node, v_node))

            node_u = self.graph_nodes.get_node_by_id(u_node)
            node_v = self.graph_nodes.get_node_by_id(v_node)

            if not node_u or not node_v:
                continue
            
            edge_count = self.graph.number_of_edges(u_node, v_node)
            
            center_u = pygame.Vector2(node_u.x, node_u.y)
            center_v = pygame.Vector2(node_v.x, node_v.y)
            
            # Tính vector hướng từ u đến v
            direction = center_v - center_u
            if direction.length() == 0:
                continue
            direction_normalized = direction.normalize()
            
            if edge_count == 1:
                # Tính điểm bắt đầu và kết thúc trên rìa của node
                start_pos = center_u + direction_normalized * node_u.radius
                end_pos = center_v - direction_normalized * node_v.radius
                
                # Vẽ đường thẳng từ rìa đến rìa
                pygame.draw.line(surface, self.border_color, start_pos, end_pos, 4)
            else:
                # Nếu có nhiều cạnh, vẽ các đường cong
                # Vector vuông góc để tạo độ cong
                normal = direction_normalized.rotate(90)
                
                for i in range(edge_count):
                    # Tính toán độ lệch cho mỗi đường cong
                    offset = (i - (edge_count - 1) / 2.0) * spacing
                    
                    # Điểm control cho đường cong Bezier (điểm giữa được dịch chuyển)
                    mid_point = center_u.lerp(center_v, 0.5) + normal * offset * 2.5
                    
                    # Tính điểm bắt đầu và kết thúc trên rìa cho đường cong
                    # Hướng từ tâm node đến điểm control để tính điểm trên rìa
                    start_dir = (mid_point - center_u).normalize()
                    end_dir = (mid_point - center_v).normalize()
                    
                    start_pos = center_u + start_dir * node_u.radius
                    end_pos = center_v + end_dir * node_v.radius
                    
                    # Vẽ đường cong Bezier bằng nhiều đoạn thẳng nhỏ
                    points = []
                    steps = 20  # Càng nhiều steps, đường cong càng mượt
                    for step in range(steps + 1):
                        t = step / steps
                        # Thuật toán De Casteljau's cho Bezier bậc 2
                        p = start_pos.lerp(mid_point, t).lerp(mid_point.lerp(end_pos, t), t)
                        points.append((p.x, p.y))
                    
                    pygame.draw.lines(surface, self.border_color, False, points, 4)

    def _handle_bridge_removal(self, point: Tuple[float, float]) -> None:
        """Xử lý việc xóa cầu khi double click."""
        closest_bridge = None
        min_distance = float('inf')
        closest_index = -1
        
        # Tìm cầu gần nhất với điểm click
        for i, (start_anchor, end_anchor) in enumerate(self.bridges):
            # Tính khoảng cách từ điểm click đến đường thẳng nối 2 anchor
            distance = self._point_to_line_distance(point, (start_anchor.x, start_anchor.y), (end_anchor.x, end_anchor.y))
            
            if distance < min_distance and distance < 15:  # Chỉ xóa nếu click đủ gần (15 pixels)
                min_distance = distance
                closest_bridge = (start_anchor, end_anchor)
                closest_index = i
        
        # Xóa cầu nếu tìm thấy
        if closest_bridge is not None:
            # Xóa khỏi danh sách cầu
            del self.bridges[closest_index]
            
            # Xóa cạnh tương ứng khỏi đồ thị
            start_node = self.REGION_TO_NODE_ID[closest_bridge[0].region]
            end_node = self.REGION_TO_NODE_ID[closest_bridge[1].region]
            
            # Xóa một cạnh giữa 2 node (trong trường hợp có nhiều cạnh)
            if self.graph.has_edge(start_node, end_node):
                self.graph.remove_edge(start_node, end_node)
            
            # Cập nhật phân tích
            self._analyze_graph()
    
    def _point_to_line_distance(self, point: Tuple[float, float], line_start: Tuple[float, float], line_end: Tuple[float, float]) -> float:
        """Tính khoảng cách từ một điểm đến một đoạn thẳng."""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector của đường thẳng
        dx = x2 - x1
        dy = y2 - y1
        
        # Nếu đường thẳng có độ dài 0
        if dx == 0 and dy == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        # Tính tham số t (vị trí trên đường thẳng gần nhất với điểm)
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        # Điểm gần nhất trên đoạn thẳng
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Khoảng cách
        return ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5

    def _is_valid_connection(self, start_anchor: BridgeAnchor, end_anchor: BridgeAnchor) -> bool:
        """Kiểm tra xem có được phép kết nối giữa 2 anchor không."""
        start_region = start_anchor.region
        end_region = end_anchor.region
        start_index = start_anchor.index
        end_index = end_anchor.index
        
        # Quy tắc kết nối point-to-point:
        
        # 1. North <-> Kneiphof: theo danh sách từ user
        if (start_region == "north" and end_region == "kneiphof") or \
           (start_region == "kneiphof" and end_region == "north"):
            # north_0->kneiphof_4, north_1->kneiphof_5, north_2->kneiphof_6, north_3->kneiphof_7
            if start_region == "north":
                if start_index < 4 and end_index >= 4 and end_index < 8:
                    expected_end = start_index + 4  # 0->4, 1->5, 2->6, 3->7
                    return end_index == expected_end
                return False
            else:  # start_region == "kneiphof"
                if start_index >= 4 and start_index < 8 and end_index < 4:
                    expected_end = start_index - 4  # 4->0, 5->1, 6->2, 7->3
                    return end_index == expected_end
                return False
        
        # 2. North <-> Lomse: theo danh sách từ user
        elif (start_region == "north" and end_region == "lomse") or \
             (start_region == "lomse" and end_region == "north"):
            # north_4->lomse_4, north_5->lomse_5, north_6->lomse_6, north_7->lomse_7
            if start_region == "north":
                if start_index >= 4 and end_index >= 4 and end_index < 8:
                    expected_end = start_index  # 4->4, 5->5, 6->6, 7->7
                    return end_index == expected_end
                return False
            else:  # start_region == "lomse"
                if start_index >= 4 and start_index < 8 and end_index >= 4:
                    expected_end = start_index  # 4->4, 5->5, 6->6, 7->7
                    return end_index == expected_end
                return False
        
        # 3. South <-> Kneiphof: theo danh sách từ user
        elif (start_region == "south" and end_region == "kneiphof") or \
             (start_region == "kneiphof" and end_region == "south"):
            # south_0->kneiphof_3, south_1->kneiphof_2, south_2->kneiphof_1, south_3->kneiphof_0
            if start_region == "south":
                if start_index < 4 and end_index < 4:
                    expected_end = 3 - start_index  # 0->3, 1->2, 2->1, 3->0
                    return end_index == expected_end
                return False
            else:  # start_region == "kneiphof"
                if start_index < 4 and end_index < 4:
                    expected_end = 3 - start_index  # 0->3, 1->2, 2->1, 3->0
                    return end_index == expected_end
                return False
        
        # 4. South <-> Lomse: theo danh sách từ user
        elif (start_region == "south" and end_region == "lomse") or \
             (start_region == "lomse" and end_region == "south"):
            # south_4->lomse_3, south_5->lomse_2, south_6->lomse_1, south_7->lomse_0
            if start_region == "south":
                if start_index >= 4 and end_index < 4:
                    expected_end = 7 - start_index  # 4->3, 5->2, 6->1, 7->0
                    return end_index == expected_end
                return False
            else:  # start_region == "lomse"
                if start_index < 4 and end_index >= 4:
                    expected_end = 7 - start_index  # 0->7, 1->6, 2->5, 3->4
                    return end_index == expected_end
                return False
        
        # 5. Kneiphof <-> Lomse: 3 điểm giữa với nhau (index ngược chiều)
        elif (start_region == "kneiphof" and end_region == "lomse") or \
             (start_region == "lomse" and end_region == "kneiphof"):
            # Kneiphof điểm 8-10 (giữa) <-> Lomse điểm 8-10 (giữa) nhưng ngược chiều
            # Kneiphof_8 <-> Lomse_10, Kneiphof_9 <-> Lomse_9, Kneiphof_10 <-> Lomse_8
            if start_region == "kneiphof":
                if start_index >= 8 and end_index >= 8:
                    # Index ngược: 8->10, 9->9, 10->8
                    expected_end = 18 - start_index  # 8+10=18, vậy 8->10, 9->9, 10->8
                    return end_index == expected_end
                return False
            else:  # start_region == "lomse"
                if start_index >= 8 and end_index >= 8:
                    # Index ngược: 8->10, 9->9, 10->8
                    expected_end = 18 - start_index  # 8+10=18, vậy 8->10, 9->9, 10->8
                    return end_index == expected_end
                return False
        
        # Tất cả các kết nối khác không được phép
        return False
    
    def _highlight_valid_targets(self, selected_anchor: BridgeAnchor) -> None:
        """Highlight tất cả các điểm có thể kết nối với điểm được chọn."""
        self.highlighted_anchors.clear()
        
        # Tìm tất cả các anchor có thể kết nối
        for anchor in self.konigsberg_map.anchor_manager.anchors:
            if anchor.region != selected_anchor.region:  # Chỉ xét các region khác
                if self._is_valid_connection(selected_anchor, anchor):
                    self.highlighted_anchors.append(anchor)

    def get_analysis_result(self) -> list[str]:
        """Trả về kết quả phân tích để MainScreen có thể hiển thị."""
        return self.analysis_result


