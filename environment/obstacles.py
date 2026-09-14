"""Obstacle and no-go region utilities."""

from dataclasses import dataclass
from math import hypot


@dataclass
class Obstacle:
    x: float
    y: float
    radius: float = 1.0
    height: float = 2.0
    blocked: bool = False
    unknown: bool = False


def distance_to_obstacle(x: float, y: float, obstacle_x: float, obstacle_y: float, radius: float) -> float:
    """Distance from a point to an obstacle boundary."""
    return hypot(x - obstacle_x, y - obstacle_y) - radius


def is_in_no_go_zone(x: float, y: float, zone):
    """Check if a point lies inside a rectangular no-go zone."""
    x_min, y_min, x_max, y_max = zone
    return x_min <= x <= x_max and y_min <= y <= y_max


def region_status(x: float, y: float, no_go_zones=None, obstacle=None):
    """Return a simple region status tag for planning decisions."""
    if no_go_zones is not None:
        for zone in no_go_zones:
            if is_in_no_go_zone(x, y, zone):
                return "blocked"

    if obstacle is not None:
        dist = distance_to_obstacle(x, y, obstacle.x, obstacle.y, obstacle.radius)
        if dist <= 0:
            return "blocked"

    return "unknown"
