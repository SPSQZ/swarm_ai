"""Individual drone in swarm with communication capabilities."""

from math import hypot


class SwarmDrone:
    def __init__(self, drone_id, x=0.0, y=0.0, z=0.0):
        self.drone_id = drone_id
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0.0
        self.vy = 0.0
        self.battery = 100
        self.mission_state = "idle"
        self.map_data = {}

    def set_position(self, x, y, z=None):
        """Update drone position."""
        self.x = x
        self.y = y
        if z is not None:
            self.z = z

    def set_velocity(self, vx, vy):
        """Update drone velocity."""
        self.vx = vx
        self.vy = vy

    def set_state(self, battery=None, mission_state=None):
        """Update drone battery and mission state."""
        if battery is not None:
            self.battery = battery
        if mission_state is not None:
            self.mission_state = mission_state

    def get_broadcast_state(self):
        """Return drone state for broadcasting to other drones."""
        return {
            "drone_id": self.drone_id,
            "position": (self.x, self.y, self.z),
            "velocity": (self.vx, self.vy),
            "battery": self.battery,
            "mission_state": self.mission_state,
        }

    def distance_to(self, other_drone):
        """Calculate distance to another drone."""
        dx = other_drone.x - self.x
        dy = other_drone.y - self.y
        dz = other_drone.z - self.z
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    def receive_map_data(self, map_data):
        """Receive and store map data from another drone."""
        self.map_data.update(map_data)
