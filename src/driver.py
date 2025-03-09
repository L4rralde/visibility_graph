from planner import VisibilityGraphPlanner
from shapes import Segment, Point

class ConstantVelocityParticle:
    def __init__(self, planner: VisibilityGraphPlanner) -> None:
        self.planner = planner
        self._speed = 0.5

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = value

    def update(self, dt: float) -> None:
        if self.planner.reached_goal():
            return

        if self._speed == 0:
            return
        shortest_path = self.planner.shortest_path()
        current = self.planner.start
        next = shortest_path[-2]

        x, y = current.x, current.y
        dx, dy = (next.x - x), (next.y - y)
        norm = (dx**2 + dy**2)**0.5
        dx, dy = dx/norm, dy/norm

        x += self._speed * dt * dx
        y += self._speed * dt * dy
        self.planner.start = Point(x, y)
