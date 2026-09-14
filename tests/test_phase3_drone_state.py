"""Tests for the Phase 3 drone state model."""

from state.drone_state import DroneState


def test_drone_state_update_and_validity():
    state = DroneState()
    state.update_state(10.0, 20.0, 5.0, 1.5, 0.5, 0.2, 0.1, 0.2, 0.3, 88.0)

    assert state.x == 10.0
    assert state.y == 20.0
    assert state.z == 5.0
    assert state.vx == 1.5
    assert state.vy == 0.5
    assert state.vz == 0.2
    assert state.yaw == 0.3
    assert state.battery == 88.0
    assert state.is_valid() is True


def test_drone_state_invalid_when_battery_is_negative():
    state = DroneState(battery=10.0)
    state.update_battery(-1.0)
    assert state.is_valid() is False


def test_drone_state_sets_mission_state():
    state = DroneState()
    state.set_mission_state("return_to_safe_zone")
    assert state.mission_state == "return_to_safe_zone"
