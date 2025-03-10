import sys

import numpy as np
from scipy.sparse import csr_array
from scipy.sparse.csgraph import dijkstra

from scene.scenes import Point, GLScene
from shapes import Segment, Polygon, Path

EPS = sys.float_info.epsilon

class VisibilityGraphPlanner:
    def __init__(
            self,
            scene: GLScene,
            start: Point,
            goal: Point,
            *args,
            **kwargs
        ) -> None:
        self.scene = scene
        self._start = start
        self._goal = goal
        self.vertices = self.get_vertices()
        self.n_vertices = len(self.vertices)
        self.graph = np.zeros((self.n_vertices + 2, self.n_vertices + 2))
        self.reset_static_graph()
        self.shortest_path = self.get_shortest_path()

    @property
    def start(self) -> Point:
        return self._start

    @start.setter
    def start(self, point: Point) -> None:
        self._start = point
        self._update_start_edges()
        self.shortest_path = self.get_shortest_path()

    def _update_start_edges(self) -> None:
        start_idx = self.n_vertices
        #Start to polygons' vertices
        for j, vertex in enumerate(self.vertices):
            segment = Segment(self._start, vertex)
            if self.is_segment_free(segment):
                self.graph[start_idx][j] = segment.len()
            else:
                self.graph[start_idx][j] = -1
        
        goal_idx = start_idx + 1
        segment = Segment(self._start, self._goal)
        if self.is_segment_free(segment):
            self.graph[goal_idx][start_idx] = segment.len()
        else:
            self.graph[goal_idx][start_idx] = -1

    @property
    def goal(self) -> Point:
        return self._goal

    @goal.setter
    def goal(self, point: Point) -> None:
        self._goal = point
        self._update_goal_edges()
        self.shortest_path = self.get_shortest_path()

    def _update_goal_edges(self) -> None:
        goal_idx = self.n_vertices + 1

        #Goal to all other vertices
        for j, vertex in enumerate(self.vertices + [self._start]):
            segment = Segment(self._goal, vertex)
            if self.is_segment_free(segment):
                self.graph[goal_idx][j] = segment.len()
            else:
                self.graph[goal_idx][j] = -1

    def get_vertices(self) -> list:
        return [
            vertex
            for polygon in self.scene.polygons
            for vertex in polygon.points
        ]

    def lines_intersect(self, line_1: Segment, line_2: Segment) -> bool:
        if line_1.points[0] in line_2.points:
            return False
        if line_1.points[1] in line_2.points:
            return False
    
        x1, y1 = line_1.points[0].x, line_1.points[0].y
        x2, y2 = line_1.points[1].x, line_1.points[1].y
        x3, y3 = line_2.points[0].x, line_2.points[0].y
        x4, y4 = line_2.points[1].x, line_2.points[1].y

        m1 = (y1 - y2)/(x1 - x2 + EPS)
        m2 = (y3 - y4)/(x3 - x4 + EPS)
        if m1 == m2:
            return False

        b1 = y1 - m1*x1
        b2 = y3 - m2*x3

        xa = (b2 - b1)/(m1 - m2)

        low_1 = min(x1, x2)
        high_1 = max(x1, x2)

        if not low_1 - EPS < xa < high_1 + EPS:
            return False
        low_2 = min(x3, x4)
        high_2 = max(x3, x4)
        if not low_2 - EPS < xa < high_2 + EPS:
            return False
        return True

    def is_segment_free(self, segment: Segment) -> bool:
        for polygon in self.scene.polygons:
            n_vertices = len(polygon.points)
            for i in range(n_vertices):
                end_a = polygon.points[i]
                end_b = polygon.points[(i + 1) % n_vertices]
                edge = Segment(end_a, end_b)
                if self.lines_intersect(segment, edge):
                    return False
        return True

    def get_vertex_polygon(self, vertex: Point) -> Polygon:
        for polygon in self.scene.polygons:
            if vertex in polygon.points:
                return polygon
        return None

    def is_inner_diagonal(
            self,
            start: Point,
            goal: Point,
            polygon: Polygon
        ) -> bool:
        n_vertices = len(polygon.points)
        start_idx = polygon.points.index(start)
        prev_start = polygon.points[(start_idx + 1) % n_vertices]
        next_to_start = polygon.points[(start_idx - 1) % n_vertices]

        angle = Segment(start, goal).angle
        prev_angle = Segment(start, prev_start).angle
        next_to_angle = Segment(start, next_to_start).angle

        while angle < next_to_angle:
            angle += 2*np.pi
        while prev_angle < next_to_angle:
            prev_angle += 2*np.pi

        return next_to_angle < angle < prev_angle
    
    def reset_static_graph(self) -> np.ndarray:
        self.graph = np.zeros((self.n_vertices + 2, self.n_vertices + 2))
        #Computing graph using polygons only
        for i in range(1, self.n_vertices):
            start = self.vertices[i]
            start_polygon = self.get_vertex_polygon(start)
            for j in range(i):
                goal = self.vertices[j]
                goal_polygon = self.get_vertex_polygon(goal)
                inner_diagonal = (
                    start_polygon == goal_polygon and
                    self.is_inner_diagonal(start, goal, start_polygon)
                )
                if inner_diagonal:
                    self.graph[i][j] = -1
                    continue
                segment = Segment(start, goal)
                if self.is_segment_free(segment):
                    self.graph[i][j] = segment.len()
                else:
                    self.graph[i][j] = -1

        #Start to polygons' vertices
        self._update_start_edges()

        #Goal to all other vertices
        self._update_goal_edges()

    def get_shortest_path(self, start: Point = None, goal: Point = None) -> list:
        if start is None:
            start = self._start
        if goal is None:
            goal = self._goal

        graph = csr_array(self.graph.T)
        graph[graph < 0] = np.inf

        j = self.n_vertices + 1
        i = self.n_vertices

        dist_matrix, predecessors = dijkstra(
            csgraph=graph,
            directed=False,
            indices = i,
            return_predecessors=True
        )
        #print(dist_matrix[self.n_vertices + 1])
        path = []

        current = j
        while current != i:
            path.append(current)
            current = predecessors[current]
            if current == -9999:
                raise ValueError("No path exists.")
        path.append(current)

        all_vertices = self.vertices + [self._start, self._goal]
        vertices_path = [all_vertices[vertex_i] for vertex_i in path]

        return Path(vertices_path)

    def reached_goal(self, th: float = 0.0005) -> bool:
        dx = self._goal.x - self._start.x
        dy = self._goal.y - self._start.y
        return dx**2 + dy**2 < th

class ReducedVisibilityGraphPlanner(VisibilityGraphPlanner):
    def __init__(
            self,
            scene: GLScene,
            start: Point,
            goal: Point,
            *args,
            **kwargs
        ) -> None:
        super().__init__(scene, start, goal, *args, **kwargs)
        self.filter_static_edges()
        self.filter_start_edges()
        self.filter_goal_edges()

    def get_vertices(self) -> list:
        #return super().get_vertices()
        vertices = []
        for polygon in self.scene.polygons:
            for i, vertex in enumerate(polygon.points):
                prev_vertex = polygon.points[(i - 1) % polygon.len]
                next_vertex = polygon.points[(i + 1) % polygon.len]
                cross = np.cross(
                    [vertex.x - prev_vertex.x, vertex.y - prev_vertex.y],
                    [next_vertex.x - vertex.x, next_vertex.y - vertex.y]
                )
                if cross > 0:
                    continue
                vertices.append(vertex)
        return vertices

    def filter_static_edges(self) -> None:
        for i in range(1, self.n_vertices):
            start = self.vertices[i]
            for j in range(i):
                goal = self.vertices[j]
                if self.graph[i][j] == -1:
                    continue
                if self.same_obstacle(start, goal):
                    continue
                if self.is_bitangent(start, goal):
                    continue
                self.graph[i][j] = -1

    def filter_start_edges(self) -> None:
        start_idx = self.n_vertices
        for j, vertex in enumerate(self.vertices):
            if self.graph[start_idx][j] == -1:
                continue
            if self.is_tangent(self._start, vertex):
                self.graph[start_idx][j] = Segment(self._start, vertex).len()
            else:
                self.graph[start_idx][j] = -1

    def filter_goal_edges(self) -> None:
        goal_idx = self.n_vertices + 1
        for j, vertex in enumerate(self.vertices):
            if self.graph[goal_idx][j] == -1:
                continue
            if self.is_tangent(self._goal, vertex):
                self.graph[goal_idx][j] = Segment(self._goal, vertex).len()
            else:
                self.graph[goal_idx][j] = -1

    def same_obstacle(self, start: Point, goal: Point) -> bool:
        start_polygon = self.get_vertex_polygon(start)
        goal_polygon = self.get_vertex_polygon(goal)
        return start_polygon == goal_polygon

    def is_bitangent(self, edga_a: Point, edga_b: Point) -> bool:
        return (
            self.is_tangent(edga_a, edga_b) and
            self.is_tangent(edga_b, edga_a)
        )

    def is_tangent(self, start: Point, goal: Point) -> bool:
        polygon = self.get_vertex_polygon(goal)
        if polygon is None:
            raise RuntimeError("Goal edge must be a polygon edge")
        goal_edge_idx = polygon.points.index(goal)
        prev_goal_edge = polygon.points[(goal_edge_idx + 1) % polygon.len]
        next_goal_edge = polygon.points[(goal_edge_idx - 1) % polygon.len]
        start_goal_disp = Segment(start, goal).displacement
        goal_prev_disp = Segment(goal, prev_goal_edge).displacement
        goal_next_disp = Segment(goal, next_goal_edge).displacement
        
        #Cross product check
        prev_cross = np.cross(start_goal_disp, goal_prev_disp)
        next_cross = np.cross(start_goal_disp, goal_next_disp)
        same_orientation = prev_cross * next_cross > 0
        return same_orientation

    @VisibilityGraphPlanner.start.setter
    def start(self, point: Point) -> None:
        VisibilityGraphPlanner.start.fset(self, point)
        self.filter_start_edges()

    @VisibilityGraphPlanner.goal.setter
    def goal(self, point: Point) -> None:
        VisibilityGraphPlanner.goal.fset(self, point)
        self.filter_goal_edges()
