"""Drone state container for the autonomy stack."""

from dataclasses import dataclass, field


@dataclass
class DroneState:
    x: float = 0.0
    y: float = 0.0
    z: float = 5.0
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    az: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    roll_rate: float = 0.0
    pitch_rate: float = 0.0
    yaw_rate: float = 0.0
    battery: float = 100.0
    mission_state: str = "explore"
    health: float = 1.0
    metadata: dict = field(default_factory=dict)

    def update_position(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def update_velocity(self, vx: float, vy: float, vz: float):
        self.vx = vx
        self.vy = vy
        self.vz = vz

    def update_acceleration(self, ax: float, ay: float, az: float):
        self.ax = ax
        self.ay = ay
        self.az = az

    def update_orientation(self, roll: float, pitch: float, yaw: float):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    def update_angular_velocity(self, roll_rate: float, pitch_rate: float, yaw_rate: float):
        self.roll_rate = roll_rate
        self.pitch_rate = pitch_rate
        self.yaw_rate = yaw_rate

    def update_battery(self, battery: float):
        self.battery = battery

    def set_mission_state(self, state: str):
        self.mission_state = state

    def update_state(self, x: float, y: float, z: float, vx: float, vy: float, vz: float, roll: float, pitch: float, yaw: float, battery: float):
        self.update_position(x, y, z)
        self.update_velocity(vx, vy, vz)
        self.update_orientation(roll, pitch, yaw)
        self.update_battery(battery)

    def is_valid(self) -> bool:
        return self.health >= 0.0 and self.battery >= 0.0 and self.z >= 0.0
