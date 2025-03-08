import sys

import numpy as np

from scene.scenes import Point, GLUtils, GLScene

EPS = sys.float_info.epsilon

class Segment:
    def __init__(self, point_i: Point, point_j: Point) -> None:
        self.points = [point_i, point_j]
    
    def draw(self) -> None:
        GLUtils.draw_line(self.points)


class Polygon:
    def __init__(self, points: list) -> None:
        if type(points[0]) == Point:
            self.points = points
        elif type(points[0]) == list:
            self.points = [Point(*point) for point in points]
        else:
            raise RuntimeError("Not recgonized data type")

    def draw(self) -> None:
        GLUtils.draw_polygon(self.points)


class PolygonScene(GLScene):
    def __init__(self, title: str, width: int, height: int, max_fps: int) -> None:
        super().__init__(title, width, height, max_fps)
        self.polygons = [
            Polygon([[-0.8, 0.2], [-0.6, 0.6], [-0.5, 0.4], [-0.15, 0.27]]),
            #Polygon([[-0.5, -0.6], [-0.8, -0.6], [-0.2, -0.4], [-0.46, -0.92]]),
            Polygon([[0.33, -0.125], [0, -0.2], [0.2, 0.2], [0.4, 0.045], [0.8, 0.2], [0.62, -0.27]])
        ]

    def render(self) -> None:
        super().render()
        for polygon in self.polygons:
            polygon.draw()

def positive_arctan2(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    return (np.arctan2(y, x) + 2*np.pi) % (2 * np.pi)


class VisibilityGraphPlanner:
    def __init__(self, scene: PolygonScene, start: Point, goal: Point) -> None:
        self.scene = scene
        self.start = start
        self.goal = goal
        self.vertices = [
            vertex
            for polygon in self.scene.polygons
            for vertex in polygon.points
        ]
        self.n_vertices = len(self.vertices)
        self.gfraph = self.get_graph()

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

        print(start_idx, next_to_angle, angle, prev_angle)
        return next_to_angle < angle < prev_angle
    
    def get_graph(self) -> np.ndarray:
        graph = -np.ones((self.n_vertices, self.n_vertices))
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
                    continue
                segment = Segment(start, goal)
                if self.is_segment_free(segment):
                    graph[i][j] = (
                        abs(start.x - goal.x) +
                        abs(start.y - goal.y)
                    )
        return graph

    def draw(self):
        for i in range(1, self.n_vertices):
            start = self.vertices[i]
            for j in range(i):
                goal = self.vertices[j]
                if self.gfraph[i][j] == -1:
                    continue
                Segment(start, goal).draw()


class VisibilityGraphScene(PolygonScene):
    def __init__(self, title: str, width: int, height: int, max_fps: int) -> None:
        super().__init__(title, width, height, max_fps)
        self.start = Point(0, 0)
        self.goal = Point(0.5, 0.5)
        self.planner = VisibilityGraphPlanner(self, self.start, self.goal)

    def render(self) -> None:
        super().render()
        self.planner.draw()

    
if __name__ == '__main__':
    scene = VisibilityGraphScene("OpenGL", 900, 600, 20)
    scene.run()
