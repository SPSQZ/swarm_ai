"""Tests for the Phase 7 sensor simulation layer."""

from sensors.sensor_base import Sensor
from sensors.simulated_sensors import SimulatedSensors


def test_sensor_reports_missing_and_failed_state():
    sensor = Sensor("gps", noise=0.1, confidence=0.8)

    sensor.update(12.0)
    assert sensor.read() == 12.1

    sensor.set_missing(True)
    assert sensor.read() is None

    sensor.set_missing(False)
    sensor.fail()
    assert sensor.is_healthy is False
    assert sensor.confidence == 0.0
    assert sensor.read() is None


def test_simulated_sensors_include_all_required_sensors():
    sensors = SimulatedSensors()

    sensors.update(
        imu=1.2,
        gps=2.3,
        altimeter=3.4,
        depth=4.5,
        lidar=5.6,
        rgb_camera=6.7,
    )

    assert sensors.imu.read() == 1.21
    assert sensors.gps.read() == 2.32
    assert sensors.altimeter.read() == 3.45
    assert sensors.depth.read() == 4.53
    assert sensors.lidar.read() == 5.62
    assert sensors.rgb_camera.read() == 6.7
