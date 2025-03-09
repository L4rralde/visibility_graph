import numpy as np
import pygame

from scene.scenes import Point, GLUtils, GLScene
from shapes import Polygon, Segment
from planner import VisibilityGraphPlanner, ReducedVisibilityGraphPlanner
from driver import ConstantVelocityParticle


default_polygons = [
    Polygon([[-0.8, 0.2], [-0.6, 0.6], [-0.5, 0.4], [-0.15, 0.27]]),
    Polygon([[-0.5, -0.6], [-0.8, -0.6], [-0.2, -0.4], [-0.46, -0.92]]),
    Polygon([[0.33, -0.12], [0, -0.2], [0.2, 0.2], [0.4, 0.04], [0.8, 0.2], [0.62, -0.27]])
]

class PolygonScene(GLScene):
    def __init__(
            self,
            title: str,
            width: int,
            height: int,
            max_fps: int = 60,
            *args,
            **kwargs
        ) -> None:
        super().__init__(title, width, height, max_fps)
        self.polygons = kwargs.get("polygons", default_polygons)
        self.shortest_path = None

    def render(self) -> None:
        super().render()
        for polygon in self.polygons:
            polygon.draw()


class VisibilityGraphScene(PolygonScene):
    def __init__(
            self,
            title: str,
            width: int,
            height: int,
            max_fps: int,
            *args,
            **kwargs
        ) -> None:
        super().__init__(title, width, height, max_fps, *args, **kwargs)
        complete = kwargs.get("complete", False)
        if complete:
            self.planner = VisibilityGraphPlanner(
                self,
                Point(-0.9, 0.9),
                Point(0.9, 0.9),
                *args,
                **kwargs
            )
        else:
            self.planner = ReducedVisibilityGraphPlanner(
                self,
                Point(-0.9, 0.9),
                Point(0.9, 0.9),
                *args,
                **kwargs
            )
        self.driver = ConstantVelocityParticle(self.planner)
        self.pause = True

    def draw_visibility_graph(self):
        for i in range(1, self.planner.n_vertices):
            start = self.planner.vertices[i]
            for j in range(i):
                goal = self.planner.vertices[j]
                if self.planner.graph[i][j] == -1:
                    continue
                Segment(start, goal).draw()

        GLUtils.draw_points([self.planner.start, self.planner.goal])

        start_idx = self.planner.n_vertices
        for j, vertex in enumerate(self.planner.vertices):
            if self.planner.graph[start_idx][j] == -1:
                continue
            Segment(self.planner.start, vertex).draw()

        goal_idx = start_idx + 1
        for j, vertex in enumerate(self.planner.vertices):
            if self.planner.graph[goal_idx][j] == -1:
                continue
            Segment(self.planner.goal, vertex).draw()

        if self.planner.graph[goal_idx][start_idx] != -1:
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause = not self.pause

    def update(self) -> None:
        super().update()
        self.shortest_path = self.planner.shortest_path()
        if not self.pause:
            self.driver.update(self.delta_time)

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
            10,
            color = (1, 1, 1, 1)
        )
