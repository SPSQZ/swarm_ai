"""World model for the drone exploration simulation."""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class TerrainCell:
    x: float
    y: float
    z: float
    slope: float = 0.0
    risk: float = 0.0


@dataclass
class Obstacle:
    x: float
    y: float
    radius: float = 1.0
    height: float = 2.0
    dynamic: bool = False


@dataclass
class DroneSpawn:
    x: float
    y: float
    z: float = 5.0


@dataclass
class SimulationClock:
    start: float = 0.0
    dt: float = 0.1
    time: float = 0.0
    tick: int = 0

    def step(self):
        self.time += self.dt
        self.tick += 1


@dataclass
class World:
    width: float = 100.0
    height: float = 100.0
    terrain_grid_size: int = 10
    terrain: List[List[TerrainCell]] = field(default_factory=list)
    static_obstacles: List[Obstacle] = field(default_factory=list)
    dynamic_obstacles: List[Obstacle] = field(default_factory=list)
    no_go_zones: List[Tuple[float, float, float, float]] = field(default_factory=list)
    drone_spawns: List[DroneSpawn] = field(default_factory=list)

    def __post_init__(self):
        self.generate_terrain()

    def generate_terrain(self):
        """Create a simple terrain grid with varying height and slope."""
        self.terrain = []
        for i in range(self.terrain_grid_size):
            row = []
            for j in range(self.terrain_grid_size):
                x = (i / max(1, self.terrain_grid_size - 1)) * self.width
                y = (j / max(1, self.terrain_grid_size - 1)) * self.height
                z = 2.0 + 0.08 * (i + j)
                slope = 0.1 + 0.03 * ((i % 5) + (j % 4))
                risk = 0.0
                row.append(TerrainCell(x=x, y=y, z=z, slope=slope, risk=risk))
            self.terrain.append(row)

    def add_static_obstacle(self, x: float, y: float, radius: float = 1.0, height: float = 2.0):
        self.static_obstacles.append(Obstacle(x=x, y=y, radius=radius, height=height, dynamic=False))

    def add_dynamic_obstacle(self, x: float, y: float, radius: float = 1.0, height: float = 2.0):
        self.dynamic_obstacles.append(Obstacle(x=x, y=y, radius=radius, height=height, dynamic=True))

    def add_drone_spawn(self, x: float, y: float, z: float = 5.0):
        self.drone_spawns.append(DroneSpawn(x=x, y=y, z=z))

    def add_no_go_zone(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.no_go_zones.append((x_min, y_min, x_max, y_max))

    def in_bounds(self, x: float, y: float) -> bool:
        return 0 <= x <= self.width and 0 <= y <= self.height
