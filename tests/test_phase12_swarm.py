"""Tests for multi-drone swarm coordination and communication."""

from swarm.drone import SwarmDrone
from swarm.swarm_coordinator import SwarmCoordinator


def test_swarm_drone_has_unique_id():
    drone1 = SwarmDrone(drone_id=1)
    drone2 = SwarmDrone(drone_id=2)

    assert drone1.drone_id == 1
    assert drone2.drone_id == 2
    assert drone1.drone_id != drone2.drone_id


def test_swarm_drone_broadcasts_state():
    drone = SwarmDrone(drone_id=1, x=5.0, y=5.0)
    drone.set_state(battery=80, mission_state="exploring")

    state = drone.get_broadcast_state()
    assert state["drone_id"] == 1
    assert state["position"] == (5.0, 5.0, 0.0)
    assert state["battery"] == 80
    assert state["mission_state"] == "exploring"


def test_swarm_coordinator_tracks_neighbors():
    coordinator = SwarmCoordinator()
    drone1 = SwarmDrone(drone_id=1, x=0.0, y=0.0)
    drone2 = SwarmDrone(drone_id=2, x=5.0, y=5.0)
    drone3 = SwarmDrone(drone_id=3, x=20.0, y=20.0)

    coordinator.add_drone(drone1)
    coordinator.add_drone(drone2)
    coordinator.add_drone(drone3)

    neighbors_of_1 = coordinator.get_neighbors(drone_id=1, comm_range=10.0)
    assert 2 in neighbors_of_1
    assert 3 not in neighbors_of_1


def test_swarm_coordinator_shares_map_data():
    coordinator = SwarmCoordinator()
    drone1 = SwarmDrone(drone_id=1)
    drone2 = SwarmDrone(drone_id=2)

    coordinator.add_drone(drone1)
    coordinator.add_drone(drone2)

    map_data = {"explored": [(1, 1), (2, 2)], "hazards": [(5, 5)]}
    coordinator.broadcast_map(source_id=1, map_data=map_data, comm_range=15.0)

    received = coordinator.get_map_data(drone_id=2)
    assert received is not None
