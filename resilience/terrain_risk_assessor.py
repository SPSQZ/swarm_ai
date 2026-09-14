"""Terrain risk assessment for exposure and difficulty calculation."""


class TerrainRiskAssessor:
    def __init__(self):
        self.slope_weight = 0.4
        self.roughness_weight = 0.3
        self.exposure_weight = 0.3
    
    def calculate_terrain_risk(self, slope, roughness, exposure):
        """Calculate overall terrain risk based on multiple factors."""
        normalized_slope = min(1.0, slope / 1.0)
        normalized_roughness = min(1.0, roughness / 1.0)
        normalized_exposure = min(1.0, exposure / 1.0)
        
        risk = (
            self.slope_weight * normalized_slope +
            self.roughness_weight * normalized_roughness +
            self.exposure_weight * normalized_exposure
        )
        
        return max(0.0, min(1.0, risk))
    
    def get_safe_corridors(self, terrain_map, risk_threshold=0.5):
        """Identify safe flight corridors in terrain map."""
        safe_cells = []
        
        for i, row in enumerate(terrain_map):
            for j, cell in enumerate(row):
                risk = self.calculate_terrain_risk(
                    cell.get("slope", 0.0),
                    cell.get("roughness", 0.0),
                    cell.get("exposure", 0.0)
                )
                if risk < risk_threshold:
                    safe_cells.append((i, j, risk))
        
        return sorted(safe_cells, key=lambda x: x[2])
    
    def calculate_sheltered_route_preference(self, current_pos, goal_pos, terrain_map):
        """Score routes based on shelter from wind and terrain exposure."""
        preference_score = 0.0
        
        dx = abs(goal_pos[0] - current_pos[0])
        dy = abs(goal_pos[1] - current_pos[1])
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance > 0:
            preference_score = 0.5
        
        return preference_score
    
    def assess_mountain_difficulty(self, altitude_delta, slope, roughness):
        """Assess difficulty of mountain terrain for drone traversal."""
        altitude_factor = min(1.0, abs(altitude_delta) / 100.0)
        slope_factor = min(1.0, slope / 0.8)
        roughness_factor = min(1.0, roughness / 0.9)
        
        difficulty = (
            altitude_factor * 0.3 +
            slope_factor * 0.4 +
            roughness_factor * 0.3
        )
        
        return max(0.0, min(1.0, difficulty))
