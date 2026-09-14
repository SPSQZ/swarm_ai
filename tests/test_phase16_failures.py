"""Tests for failure simulation and graceful degradation."""

from resilience.failure_simulator import FailureSimulator
from resilience.sensor_failures import SensorFailureManager
from resilience.communication_failures import CommunicationFailureManager


def test_failure_simulator_creates_gps_loss():
    simulator = FailureSimulator()
    simulator.inject_failure("gps_loss", drone_id=1, duration=10)
    
    failures = simulator.get_active_failures(drone_id=1)
    assert any(f["type"] == "gps_loss" for f in failures)


def test_failure_simulator_creates_sensor_noise_increase():
    simulator = FailureSimulator()
    simulator.inject_failure("sensor_noise_spike", drone_id=2, severity=0.8)
    
    failures = simulator.get_active_failures(drone_id=2)
    assert len(failures) > 0


def test_sensor_failure_manager_degrades_gps():
    manager = SensorFailureManager()
    manager.simulate_gps_failure(failure_probability=1.0)
    
    is_healthy = manager.is_gps_healthy()
    assert is_healthy is False


def test_sensor_failure_manager_increases_noise():
    manager = SensorFailureManager()
    noise_normal = manager.get_sensor_noise("imu")
    
    manager.simulate_sensor_noise_increase("imu", multiplier=3.0)
    noise_increased = manager.get_sensor_noise("imu")
    
    assert noise_increased > noise_normal


def test_communication_failure_manager_simulates_packet_loss():
    manager = CommunicationFailureManager()
    manager.set_packet_loss_rate(0.5)
    
    packet_lost_count = 0
    for _ in range(100):
        if manager.should_drop_packet():
            packet_lost_count += 1
    
    assert 30 < packet_lost_count < 70


def test_communication_failure_manager_simulates_link_outage():
    manager = CommunicationFailureManager()
    manager.simulate_link_outage(drone_id=1, duration=5)
    
    is_connected = manager.is_drone_connected(drone_id=1)
    assert is_connected is False
