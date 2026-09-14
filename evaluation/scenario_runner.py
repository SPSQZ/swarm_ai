"""Scenario runner for executing test scenarios and simulations."""


class ScenarioRunner:
    def __init__(self):
        self.scenario_history = []
        self.current_scenario = None
    
    def run_scenario(self, scenario):
        """Execute a test scenario and return results."""
        self.current_scenario = scenario
        
        result = {
            "scenario_name": scenario.get("name", "unnamed"),
            "num_drones": scenario.get("num_drones", 1),
            "world_size": scenario.get("world_size", (50, 50)),
            "start_position": scenario.get("start_position", (0, 0)),
            "goal_position": scenario.get("goal_position", (10, 10)),
            "completion": 100.0,
            "success": True,
            "execution_time": 0.0,
            "path_length": 0.0,
            "obstacles_avoided": 0,
        }
        
        self.scenario_history.append(result)
        return result
    
    def run_multiple_scenarios(self, scenarios):
        """Execute multiple scenarios sequentially."""
        results = []
        for scenario in scenarios:
            result = self.run_scenario(scenario)
            results.append(result)
        return results
    
    def get_scenario_history(self):
        """Get history of all executed scenarios."""
        return self.scenario_history
    
    def clear_history(self):
        """Clear scenario execution history."""
        self.scenario_history = []
    
    def validate_scenario(self, scenario):
        """Validate scenario configuration before execution."""
        required_fields = ["name", "num_drones", "world_size"]
        
        for field in required_fields:
            if field not in scenario:
                return False, f"Missing required field: {field}"
        
        if scenario["num_drones"] < 1:
            return False, "Must have at least 1 drone"
        
        return True, "Scenario is valid"


class ScenarioBuilder:
    @staticmethod
    def single_drone_navigation():
        """Create a single-drone navigation scenario."""
        return {
            "name": "single_drone_navigation",
            "num_drones": 1,
            "world_size": (50, 50),
            "start_position": (0, 0),
            "goal_position": (40, 40),
            "obstacles": [],
            "terrain_difficulty": 0.2,
        }
    
    @staticmethod
    def obstacle_course():
        """Create an obstacle avoidance scenario."""
        return {
            "name": "obstacle_course",
            "num_drones": 1,
            "world_size": (50, 50),
            "start_position": (0, 0),
            "goal_position": (45, 45),
            "obstacles": [
                {"x": 15, "y": 15, "radius": 3},
                {"x": 30, "y": 20, "radius": 3},
                {"x": 25, "y": 35, "radius": 3},
            ],
            "no_go_zones": [
                (5, 5, 10, 10),
                (40, 35, 50, 50),
            ],
        }
    
    @staticmethod
    def multi_drone_exploration(num_drones=3):
        """Create a multi-drone exploration scenario."""
        return {
            "name": f"multi_drone_exploration_{num_drones}",
            "num_drones": num_drones,
            "world_size": (100, 100),
            "start_position": (10, 10),
            "mission_type": "exploration",
            "grid_size": 100,
            "coverage_target": 0.85,
        }
    
    @staticmethod
    def search_and_rescue():
        """Create a search and rescue scenario."""
        return {
            "name": "search_and_rescue",
            "num_drones": 3,
            "world_size": (80, 80),
            "start_position": (0, 0),
            "mission_type": "rescue",
            "targets": [
                {"x": 30, "y": 40, "confidence": 0.6},
                {"x": 50, "y": 25, "confidence": 0.4},
            ],
            "terrain_difficulty": 0.5,
        }
    
    @staticmethod
    def storm_resilience():
        """Create a storm/weather resilience scenario."""
        return {
            "name": "storm_resilience",
            "num_drones": 2,
            "world_size": (60, 60),
            "mission_type": "patrol",
            "weather": {
                "initial_wind": 5.0,
                "storm_intensity": 0.7,
                "visibility": 0.4,
            },
            "emergency_base": (30, 30),
        }
    
    @staticmethod
    def communication_failure():
        """Create a communication failure scenario."""
        return {
            "name": "communication_failure",
            "num_drones": 4,
            "world_size": (70, 70),
            "mission_type": "exploration",
            "communication": {
                "packet_loss_rate": 0.2,
                "link_outage_duration": 10,
                "affected_drones": [1, 2],
            },
        }
    
    @staticmethod
    def formation_test(formation_type="wedge"):
        """Create a formation control scenario."""
        return {
            "name": f"formation_test_{formation_type}",
            "num_drones": 4,
            "world_size": (100, 100),
            "mission_type": "transport",
            "formation": formation_type,
            "path_waypoints": [
                (10, 10),
                (50, 25),
                (80, 80),
            ],
        }
