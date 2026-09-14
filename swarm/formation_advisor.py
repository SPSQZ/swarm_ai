"""Formation advisor for mission-specific and context-aware formation selection."""


class FormationAdvisor:
    def __init__(self):
        self.mission_profiles = {
            "rescue": {
                "primary_formation": "wedge",
                "spacing": 1.5,
                "speed_priority": "quick_response",
                "energy_priority": "moderate",
            },
            "exploration": {
                "primary_formation": "arc",
                "spacing": 2.5,
                "speed_priority": "coverage",
                "energy_priority": "low",
            },
            "surveillance": {
                "primary_formation": "diamond",
                "spacing": 2.0,
                "speed_priority": "smooth",
                "energy_priority": "moderate",
            },
            "transport": {
                "primary_formation": "line",
                "spacing": 3.0,
                "speed_priority": "distance",
                "energy_priority": "high",
            },
            "search": {
                "primary_formation": "wedge",
                "spacing": 2.0,
                "speed_priority": "coverage",
                "energy_priority": "low",
            },
        }
    
    def get_formation_for_mission(self, mission_type, num_drones, energy_available):
        """Get recommended formation and parameters for a specific mission."""
        profile = self.mission_profiles.get(mission_type, self.mission_profiles["exploration"])
        
        formation = profile["primary_formation"]
        spacing = profile["spacing"]
        
        if energy_available < 40:
            spacing *= 0.8
            if mission_type != "rescue":
                formation = "line"
        
        return {
            "mission_type": mission_type,
            "formation": formation,
            "num_drones": num_drones,
            "spacing": spacing,
            "speed_priority": profile["speed_priority"],
            "energy_priority": profile["energy_priority"],
            "energy_available": energy_available,
        }
    
    def get_alternative_formations(self, mission_type, num_drones):
        """Get alternative formation options for a mission."""
        primary = self.get_formation_for_mission(mission_type, num_drones, 100.0)
        
        alternatives = []
        if mission_type == "rescue":
            alternatives = ["line", "arc"]
        elif mission_type == "exploration":
            alternatives = ["line", "diamond"]
        elif mission_type == "surveillance":
            alternatives = ["arc", "wedge"]
        elif mission_type == "transport":
            alternatives = ["wedge", "arc"]
        
        return {
            "primary": primary["formation"],
            "alternatives": alternatives,
            "recommendations": primary,
        }
    
    def evaluate_formation_efficiency(self, formation, num_drones, energy_cost_map):
        """Evaluate formation efficiency based on energy costs."""
        efficiency_score = {
            "line": 0.85,
            "wedge": 0.75,
            "arc": 0.65,
            "diamond": 0.70,
        }
        
        base_score = efficiency_score.get(formation, 0.5)
        
        if num_drones <= 2:
            base_score *= 0.9
        elif num_drones <= 4:
            base_score *= 1.0
        elif num_drones <= 8:
            base_score *= 0.95
        else:
            base_score *= 0.85
        
        return {
            "formation": formation,
            "efficiency_score": base_score,
            "num_drones": num_drones,
            "formation_type_score": efficiency_score.get(formation),
        }
