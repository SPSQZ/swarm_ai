"""Container for the simulated sensor set for the drone."""

from sensors.sensor_base import Sensor


class SimulatedSensors:
    def __init__(self):
        self.imu = Sensor("imu", noise=0.01, confidence=0.95)
        self.gps = Sensor("gps", noise=0.02, confidence=0.9)
        self.altimeter = Sensor("altimeter", noise=0.05, confidence=0.92)
        self.depth = Sensor("depth", noise=0.03, confidence=0.88)
        self.lidar = Sensor("lidar", noise=0.02, confidence=0.96)
        self.rgb_camera = Sensor("rgb_camera", noise=0.0, confidence=0.9)

    def update(
        self,
        imu=0.0,
        gps=0.0,
        altimeter=0.0,
        depth=0.0,
        lidar=0.0,
        rgb_camera=0.0,
    ):
        self.imu.update(imu)
        self.gps.update(gps)
        self.altimeter.update(altimeter)
        self.depth.update(depth)
        self.lidar.update(lidar)
        self.rgb_camera.update(rgb_camera)
