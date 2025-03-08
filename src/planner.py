import sys

import numpy as np

from scene.scenes import Point, GLScene
from shapes import Segment, Polygon

EPS = sys.float_info.epsilon

class VisibilityGraphPlanner:
    def __init__(self, scene: GLScene, start: Point, goal: Point) -> None:
        self.scene = scene
        self._start = start
        self._goal = goal
        self.vertices = [
            vertex
            for polygon in self.scene.polygons
            for vertex in polygon.points
        ]
        self.n_vertices = len(self.vertices)
        self.graph = np.zeros((self.n_vertices + 2, self.n_vertices + 2))
        self.reset_static_graph()

    @property
    def start(self) -> Point:
        return self._start

    @start.setter
    def start(self, point: Point) -> None:
        self._start = point
        self._update_start_edges()

    def _update_start_edges(self) -> None:
        #Start to polygons' vertices
        for j, vertex in enumerate(self.vertices):
            segment = Segment(self._start, vertex)
            if self.is_segment_free(segment):
                self.graph[self.n_vertices][j] = segment.len()
            else:
                self.graph[self.n_vertices][j] = -1
        
        segment = Segment(self._start, self._goal)
        if self.is_segment_free(segment):
            self.graph[self.n_vertices + 1][self.n_vertices] = segment.len()
        else:
            self.graph[self.n_vertices + 1][self.n_vertices] = -1

    @property
    def goal(self) -> Point:
        return self._goal

    @goal.setter
    def goal(self, point: Point) -> None:
        self._goal = point
        self._update_goal_edges()

    def _update_goal_edges(self) -> None:
        #Goal to all other vertices
        for j, vertex in enumerate(self.vertices + [self._start]):
            segment = Segment(self._goal, vertex)
            if self.is_segment_free(segment):
                self.graph[self.n_vertices + 1][j] = segment.len()
            else:
                self.graph[self.n_vertices + 1][j] = -1


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

    def is_inner_diagonal(self, start: Point, goal: Point, polygon: Polygon) -> bool:
        n_vertices = len(polygon.points)
        start_idx = polygon.points.index(start)
        prev_start = polygon.points[(start_idx + 1) % n_vertices]
        next_to_start = polygon.points[(start_idx - 1) % n_vertices]

        angle = np.arctan2(goal.y - start.y, goal.x - start.x)
        prev_angle = np.arctan2(prev_start.y - start.y, prev_start.x - start.x)
        next_to_angle = np.arctan2(
            next_to_start.y - start.y,
            next_to_start.x - start.x
        )
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

