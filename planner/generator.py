"""Candidate path generation primitives for a simulated drone."""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Trajectory:
    name: str
    points: List[Tuple[float, float]]
    altitude: float
    speed: float = 1.0
    velocity_limit: float = 5.0
    acceleration_limit: float = 2.0
    min_clearance: float = 1.0
    params: dict = field(default_factory=dict)


class PathGenerator:
    def generate_straight(self, start, goal, altitude=5.0, speed=1.0):
        return Trajectory(
            name="straight",
            points=[start, goal],
            altitude=altitude,
            speed=speed,
            params={"type": "straight"},
        )

    def generate_turn(self, start, goal, altitude=5.0, speed=1.0):
        turn_point = ((start[0] + goal[0]) / 2, (start[1] + goal[1]) / 2)
        return Trajectory(
            name="turn",
            points=[start, turn_point, goal],
            altitude=altitude,
            speed=speed,
            params={"type": "turn"},
        )

    def generate_climb(self, start, goal, altitude=7.0, speed=1.0):
        return Trajectory(
            name="climb",
            points=[start, goal],
            altitude=altitude,
            speed=speed,
            params={"type": "climb"},
        )

    def generate_descend(self, start, goal, altitude=3.0, speed=1.0):
        return Trajectory(
            name="descend",
            points=[start, goal],
            altitude=altitude,
            speed=speed,
            params={"type": "descend"},
        )

    def generate_hover(self, position, altitude=5.0, speed=0.0):
        return Trajectory(
            name="hover",
            points=[position],
            altitude=altitude,
            speed=speed,
            params={"type": "hover"},
        )

    def generate_candidates(self, start, goal):
        return [
            self.generate_straight(start, goal),
            self.generate_turn(start, goal),
            self.generate_climb(start, goal),
            self.generate_descend(start, goal),
        ]

    def sample_trajectory(self, trajectory, steps=10):
        if len(trajectory.points) < 2:
            return [trajectory.points[0]] if trajectory.points else []

        sampled = []
        for i in range(steps + 1):
            t = i / max(1, steps)
            x0, y0 = trajectory.points[0]
            x1, y1 = trajectory.points[-1]
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            sampled.append((x, y))
        return sampled

    def is_valid(self, trajectory, min_clearance=1.0):
        return trajectory.min_clearance >= min_clearance and trajectory.speed >= 0.0
