"""Metrics collection and analysis for drone system evaluation."""


class MetricsCollector:
    def __init__(self):
        self.position_history = {}
        self.visited_cells = set()
        self.collision_count = 0
        self.battery_usage = {}
        self.mission_events = []
    
    def record_position(self, drone_id, x, y, z=0):
        """Record drone position at a timestep."""
        if drone_id not in self.position_history:
            self.position_history[drone_id] = []
        
        self.position_history[drone_id].append({"x": x, "y": y, "z": z})
    
    def record_collision(self):
        """Record a collision event."""
        self.collision_count += 1
    
    def record_battery_usage(self, drone_id, battery_percent):
        """Record battery level for a drone."""
        if drone_id not in self.battery_usage:
            self.battery_usage[drone_id] = []
        
        self.battery_usage[drone_id].append(battery_percent)
    
    def mark_cell_visited(self, x, y):
        """Mark a grid cell as visited during exploration."""
        self.visited_cells.add((int(x), int(y)))
    
    def record_event(self, event_type, drone_id, details):
        """Record a mission event (target found, obstacle hit, etc.)."""
        self.mission_events.append({
            "type": event_type,
            "drone_id": drone_id,
            "details": details,
        })
    
    def get_total_distance(self, drone_id):
        """Calculate total distance traveled by a drone."""
        if drone_id not in self.position_history:
            return 0.0
        
        positions = self.position_history[drone_id]
        if len(positions) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(positions) - 1):
            p1 = positions[i]
            p2 = positions[i + 1]
            
            dx = p2["x"] - p1["x"]
            dy = p2["y"] - p1["y"]
            dz = p2["z"] - p1["z"]
            
            distance = (dx**2 + dy**2 + dz**2) ** 0.5
            total_distance += distance
        
        return total_distance
    
    def get_coverage_percentage(self, grid_width=10, grid_height=10):
        """Calculate coverage percentage of exploration area."""
        total_cells = grid_width * grid_height
        if total_cells == 0:
            return 0.0
        
        coverage = len(self.visited_cells) / total_cells
        return min(1.0, coverage) * 100.0
    
    def get_average_speed(self, drone_id):
        """Calculate average speed for a drone."""
        distance = self.get_total_distance(drone_id)
        time_steps = len(self.position_history.get(drone_id, []))
        
        if time_steps < 2:
            return 0.0
        
        return distance / (time_steps - 1)
    
    def get_battery_efficiency(self, drone_id):
        """Calculate battery efficiency (distance per unit battery)."""
        if drone_id not in self.battery_usage:
            return 0.0
        
        battery_usage = self.battery_usage[drone_id]
        if len(battery_usage) < 2:
            return 0.0
        
        battery_consumed = battery_usage[0] - battery_usage[-1]
        distance = self.get_total_distance(drone_id)
        
        if battery_consumed == 0:
            return 0.0
        
        return distance / battery_consumed
    
    def get_mission_events_summary(self):
        """Get summary of mission events."""
        event_summary = {}
        
        for event in self.mission_events:
            event_type = event["type"]
            event_summary[event_type] = event_summary.get(event_type, 0) + 1
        
        return event_summary
    
    def get_collision_rate(self):
        """Get total collision count."""
        return self.collision_count
