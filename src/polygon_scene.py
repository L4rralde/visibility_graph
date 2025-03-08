import numpy as np
import pygame

from scene.scenes import Point, GLUtils, GLScene
from shapes import Polygon, Segment
from planner import VisibilityGraphPlanner


class PolygonScene(GLScene):
    def __init__(self, title: str, width: int, height: int, max_fps: int) -> None:
        super().__init__(title, width, height, max_fps)
        self.polygons = [
            Polygon([[-0.8, 0.2], [-0.6, 0.6], [-0.5, 0.4], [-0.15, 0.27]]),
            Polygon([[-0.5, -0.6], [-0.8, -0.6], [-0.2, -0.4], [-0.46, -0.92]]),
            Polygon([[0.33, -0.125], [0, -0.2], [0.2, 0.2], [0.4, 0.045], [0.8, 0.2], [0.62, -0.27]])
        ]
        self.shortest_path = None

    def render(self) -> None:
        super().render()
        for polygon in self.polygons:
            polygon.draw()

def positive_arctan2(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    return (np.arctan2(y, x) + 2*np.pi) % (2 * np.pi)


class VisibilityGraphScene(PolygonScene):
    def __init__(self, title: str, width: int, height: int, max_fps: int, *args, **kwargs) -> None:
        super().__init__(title, width, height, max_fps)
        complete = kwargs.get("complete", False)
        self.planner = VisibilityGraphPlanner(self, Point(-0.9, 0.9), Point(0.9, 0.9), complete)

    def draw_visibility_graph(self):
        for i in range(1, self.planner.n_vertices):
            start = self.planner.vertices[i]
            for j in range(i):
                goal = self.planner.vertices[j]
                if self.planner.graph[i][j] == -1:
                    continue
                Segment(start, goal).draw()

        GLUtils.draw_points([self.planner.start, self.planner.goal])
        for j, vertex in enumerate(self.planner.vertices):
            if self.planner.graph[self.planner.n_vertices][j] == -1:
                continue
            Segment(self.planner.start, vertex).draw()

        for j, vertex in enumerate(self.planner.vertices):
            if self.planner.graph[self.planner.n_vertices + 1][j] == -1:
                continue
            Segment(self.planner.goal, vertex).draw()

        if self.planner.graph[self.planner.n_vertices + 1][self.planner.n_vertices] != -1:
            Segment(self.planner.goal, self.planner.start).draw()

    def get_inputs(self) -> None:
        super().get_inputs()
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                screen_point = Point(x, y)
                ortho = self.to_ortho(screen_point)
                ortho.y *= -1
                if event.button == 1: #Left click
                    self.planner.start = ortho
                if event.button == 3: #Right click
                    self.planner.goal = ortho

    def update(self) -> None:
        super().update()
        self.shortest_path = self.planner.shortest_path()

    def render(self) -> None:
        super().render()
        self.draw_visibility_graph()
        self.shortest_path.draw()
        GLUtils.draw_point(
            self.planner.start.x,
            self.planner.start.y,
            5,
            color = (1, 1, 1, 1)
        )
        GLUtils.draw_point(
            self.planner.goal.x,
            self.planner.goal.y,
            15,
            color = (0.8, 0.8, 0.8, 1)
        )