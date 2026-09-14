"""Terrain utilities for terrain slope and risk scoring."""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TerrainCell:
    x: float
    y: float
    height: float
    slope: float = 0.0
    roughness: float = 0.0
    risk: float = 0.0
    blocked: bool = False
    unknown: bool = False


@dataclass
class Environment:
    width: float
    height: float
    cells: List[List[TerrainCell]] = None
    no_go_zones: List[Tuple[float, float, float, float]] = None

    def __post_init__(self):
        if self.cells is None:
            self.cells = []
        if self.no_go_zones is None:
            self.no_go_zones = []

    def add_no_go_zone(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.no_go_zones.append((x_min, y_min, x_max, y_max))

    def get_cell(self, x: float, y: float, grid_size: int = 10):
        ix = min(grid_size - 1, max(0, int(x / max(1.0, self.width / grid_size))))
        iy = min(grid_size - 1, max(0, int(y / max(1.0, self.height / grid_size))))
        if 0 <= ix < len(self.cells) and 0 <= iy < len(self.cells[0]):
            return self.cells[ix][iy]
        return None


def terrain_slope(height_a: float, height_b: float, distance: float) -> float:
    """Estimate local slope between two terrain heights."""
    if distance <= 0:
        return 0.0
    return abs(height_b - height_a) / distance


def terrain_risk(slope: float, roughness: float = 0.0, obstacle_cost: float = 0.0) -> float:
    """Combine geometry and obstacle risk into a simple terrain-risk score."""
    return min(1.0, slope * 0.6 + roughness * 0.3 + obstacle_cost * 0.1)


def generate_terrain_grid(width: float, height: float, grid_size: int = 10):
    """Generate a simple terrain grid with varying slopes and height values."""
    cells = []
    for i in range(grid_size):
        row = []
        for j in range(grid_size):
            x = (i / max(1, grid_size - 1)) * width
            y = (j / max(1, grid_size - 1)) * height
            height_value = 2.0 + 0.08 * (i + j)
            slope = 0.1 + 0.03 * ((i % 5) + (j % 4))
            risk = terrain_risk(slope=slope, roughness=0.1)
            row.append(TerrainCell(x=x, y=y, height=height_value, slope=slope, roughness=0.1, risk=risk))
        cells.append(row)
    return cells
