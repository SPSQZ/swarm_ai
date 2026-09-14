"""Intelligent formation planning that adapts based on mission context and environmental factors."""

from math import cos, sin, pi


class IntelligentFormationPlanner:
    def __init__(self, num_drones=4):
        self.num_drones = num_drones
        self.formation_scores = {}
        
    def select_formation(self, mission_context):
        """Select optimal formation based on mission parameters and environmental factors."""
        mission_type = mission_context.get("mission_type", "exploration")
        energy = mission_context.get("energy_available", 100.0)
        terrain_difficulty = mission_context.get("terrain_difficulty", 0.5)
        wind_speed = mission_context.get("wind_speed", 0.0)
        num_obstacles = mission_context.get("num_obstacles", 0)
        
        formations = ["line", "wedge", "arc", "diamond"]
        best_formation = None
        best_score = -1
        
        for formation in formations:
            score = self._score_formation(
                formation, mission_type, energy, 
                terrain_difficulty, wind_speed, num_obstacles
            )
            if score > best_score:
                best_score = score
                best_formation = formation
        
        offsets = self._get_formation_offsets(best_formation)
        return {
            "type": best_formation,
            "offsets": offsets,
            "spacing": 3.0,
            "efficiency_score": best_score,
        }
    
    def _score_formation(self, formation, mission_type, energy, terrain_diff, wind, obstacles):
        """Score a formation based on mission requirements and constraints."""
        score = 50.0
        
        if mission_type == "rescue":
            if formation == "wedge":
                score += 30
            elif formation == "line":
                score += 15
        elif mission_type == "exploration":
            if formation == "arc":
                score += 25
            elif formation == "line":
                score += 20
        elif mission_type == "surveillance":
            if formation == "diamond":
                score += 30
            elif formation == "arc":
                score += 15
        
        if energy < 30:
            if formation in ["line", "wedge"]:
                score += 20
            else:
                score -= 10
        
        if terrain_diff > 0.7:
            if formation == "wedge":
                score += 15
            elif formation == "line":
                score -= 10
        
        if wind > 10:
            if formation == "line":
                score -= 20
            elif formation == "diamond":
                score += 15
        
        if obstacles > 3:
            if formation == "arc":
                score += 20
            elif formation == "wedge":
                score += 10
        
        return max(0, score)
    
    def _get_formation_offsets(self, formation_type):
        """Get standard offsets for formation type."""
        spacing = 2.0
        if formation_type == "line":
            return [(i * spacing, 0) for i in range(self.num_drones)]
        elif formation_type == "wedge":
            offsets = [(0, 0)]
            for i in range(1, self.num_drones):
                side = -1 if i % 2 == 1 else 1
                row = (i + 1) // 2
                offsets.append((row * spacing, side * row * spacing / 2))
            return offsets[:self.num_drones]
        elif formation_type == "diamond":
            return [
                (0, 0),
                (-spacing, -spacing),
                (spacing, -spacing),
                (0, -2 * spacing),
            ][:self.num_drones]
        elif formation_type == "arc":
            offsets = []
            radius = spacing * 2
            for i in range(self.num_drones):
                angle = (i / max(1, self.num_drones - 1)) * pi
                x = radius * cos(angle)
                y = radius * sin(angle)
                offsets.append((x, y))
            return offsets
        return [(0, 0)] * self.num_drones
    
    def adapt_formation_for_wind(self, wind_speed, base_formation):
        """Adapt formation spacing and orientation based on wind conditions."""
        adaptation = {
            "formation": base_formation,
            "spacing_multiplier": 1.0,
            "orientation_offset": 0.0,
            "stability_rating": 1.0,
        }
        
        if wind_speed < 5:
            adaptation["spacing_multiplier"] = 1.0
            adaptation["stability_rating"] = 0.95
        elif wind_speed < 10:
            adaptation["spacing_multiplier"] = 1.2
            adaptation["stability_rating"] = 0.85
        elif wind_speed < 15:
            adaptation["spacing_multiplier"] = 1.5
            adaptation["stability_rating"] = 0.70
        else:
            adaptation["spacing_multiplier"] = 2.0
            adaptation["stability_rating"] = 0.50
            if base_formation == "line":
                adaptation["formation"] = "wedge"
        
        return adaptation
    
    def optimize_formation_for_energy(self, formation, battery_level, distance_to_travel):
        """Optimize formation for energy efficiency given battery constraints."""
        optimization = {
            "formation": formation,
            "spacing_adjustment": 1.0,
            "speed_adjustment": 1.0,
            "energy_efficiency": 0.8,
        }
        
        total_battery_cost = battery_level / max(1, distance_to_travel)
        
        if battery_level > 80:
            optimization["spacing_adjustment"] = 1.0
            optimization["energy_efficiency"] = 0.9
        elif battery_level > 50:
            optimization["spacing_adjustment"] = 0.9
            optimization["speed_adjustment"] = 0.95
            optimization["energy_efficiency"] = 0.85
        elif battery_level > 30:
            optimization["spacing_adjustment"] = 0.7
            optimization["speed_adjustment"] = 0.8
            optimization["energy_efficiency"] = 0.70
        else:
            if formation != "line":
                optimization["formation"] = "line"
            optimization["spacing_adjustment"] = 0.5
            optimization["speed_adjustment"] = 0.6
            optimization["energy_efficiency"] = 0.50
        
        return optimization
