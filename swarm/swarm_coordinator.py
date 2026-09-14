"""Swarm coordinator for multi-drone communication and coordination."""

from math import hypot


class SwarmCoordinator:
    def __init__(self):
        self.drones = {}
        self.shared_maps = {}
        self.hazard_reports = {}

    def add_drone(self, drone):
        """Add a drone to the swarm."""
        self.drones[drone.drone_id] = drone
        self.shared_maps[drone.drone_id] = {}

    def get_neighbors(self, drone_id, comm_range=15.0):
        """Find neighbors of a drone within communication range."""
        if drone_id not in self.drones:
            return []

        source_drone = self.drones[drone_id]
        neighbors = []

        for other_id, other_drone in self.drones.items():
            if other_id != drone_id:
                dist = source_drone.distance_to(other_drone)
                if dist <= comm_range:
                    neighbors.append(other_id)

        return neighbors

    def broadcast_state(self, drone_id):
        """Broadcast a drone's state to all neighbors."""
        if drone_id not in self.drones:
            return

        drone = self.drones[drone_id]
        state = drone.get_broadcast_state()
        return state

    def broadcast_map(self, source_id, map_data, comm_range=15.0):
        """Broadcast map data from one drone to neighbors."""
        neighbors = self.get_neighbors(source_id, comm_range)

        for neighbor_id in neighbors:
            if neighbor_id in self.drones:
                self.drones[neighbor_id].receive_map_data(map_data)
                self.shared_maps[neighbor_id].update(map_data)

    def get_map_data(self, drone_id):
        """Retrieve accumulated map data for a drone."""
        return self.shared_maps.get(drone_id, {})

    def report_hazard(self, drone_id, hazard_location):
        """Report a hazard discovery to the swarm."""
        if drone_id not in self.hazard_reports:
            self.hazard_reports[drone_id] = []
        self.hazard_reports[drone_id].append(hazard_location)

    def get_all_hazards(self):
        """Return all reported hazards from the swarm."""
        all_hazards = []
        for hazards in self.hazard_reports.values():
            all_hazards.extend(hazards)
        return all_hazards
