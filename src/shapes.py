from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from scene.scenes import Point, GLUtils

class Segment:
    def __init__(self, point_i: Point, point_j: Point) -> None:
        self.points = [point_i, point_j]
    
    def draw(self) -> None:
        GLUtils.draw_line(self.points)

    def len(self) -> float:
        return (
            (self.points[0].x - self.points[1].x)**2 +
            (self.points[0].y - self.points[1].y)**2
        )**0.5

    @property
    def displacement(self) -> list:
        return [
            self.points[1].y - self.points[0].y,
            self.points[1].x - self.points[0].x
        ]

    @property
    def angle(self) -> float:
        return np.arctan2(
            self.points[1].y - self.points[0].y,
            self.points[1].x - self.points[0].x
        )

class Polygon:
    def __init__(self, points: list) -> None:
        if type(points[0]) == Point:
            self.points = points
        elif type(points[0]) == list:
            self.points = [Point(*point) for point in points]
        else:
            raise RuntimeError("Not recgonized data type")
        self.len = len(self.points)

    def draw(self) -> None:
        GLUtils.draw_polygon(self.points)


class Path:
    def __init__(self, points: list) -> None:
        self.points = points

    def draw(self) -> None:
        GLUtils.draw_line(
            self.points,
            size=2,
            color=(0.5, 0.5, 0.5, 1)
        )
