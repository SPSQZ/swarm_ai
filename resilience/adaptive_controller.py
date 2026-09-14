"""Adaptive drone controller for dynamic response to weather and terrain changes."""


class AdaptiveController:
    def __init__(self):
        self.max_safe_wind = 15.0
        self.min_safe_visibility = 0.2
        self.emergency_wind_threshold = 18.0
        self.emergency_visibility_threshold = 0.05
    
    def calculate_safe_speed(self, wind_speed, visibility, base_speed=2.0):
        """Calculate safe flight speed based on weather conditions."""
        speed = base_speed
        
        if wind_speed > 10:
            speed *= (1.0 - (wind_speed - 10.0) / 20.0)
        
        if visibility < 0.5:
            speed *= visibility
        
        return max(0.1, speed)
    
    def adapt_formation_spacing(self, base_spacing, weather_risk, terrain_risk):
        """Contract formation spacing when conditions are risky."""
        combined_risk = (weather_risk + terrain_risk) / 2.0
        
        if combined_risk < 0.3:
            spacing_multiplier = 1.0
        elif combined_risk < 0.5:
            spacing_multiplier = 0.9
        elif combined_risk < 0.7:
            spacing_multiplier = 0.7
        else:
            spacing_multiplier = 0.5
        
        return base_spacing * spacing_multiplier
    
    def should_trigger_emergency_hold(self, wind_speed, visibility, battery_level):
        """Determine if emergency landing/hold should be triggered."""
        if wind_speed >= self.emergency_wind_threshold:
            return True
        
        if visibility <= self.emergency_visibility_threshold:
            return True
        
        if battery_level <= 15:
            return True
        
        return False
    
    def calculate_return_to_base_route(self, current_pos, base_pos, weather_risk):
        """Calculate safest route back to base given weather conditions."""
        dx = base_pos[0] - current_pos[0]
        dy = base_pos[1] - current_pos[1]
        
        straight_distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if weather_risk > 0.7:
            safe_distance = straight_distance * 1.3
            detour_factor = 1 + (weather_risk * 0.5)
        else:
            safe_distance = straight_distance * (1 + weather_risk * 0.2)
            detour_factor = 1.0
        
        return {
            "route": "diagonal_with_detour" if detour_factor > 1.1 else "direct",
            "estimated_distance": safe_distance,
            "detour_factor": detour_factor,
            "waypoints": self._generate_waypoints(current_pos, base_pos, weather_risk),
        }
    
    def _generate_waypoints(self, current_pos, base_pos, weather_risk):
        """Generate intermediate waypoints for safe return."""
        waypoints = [current_pos]
        
        mid_x = (current_pos[0] + base_pos[0]) / 2
        mid_y = (current_pos[1] + base_pos[1]) / 2
        
        if weather_risk > 0.5:
            offset = weather_risk * 5
            waypoints.append((mid_x - offset, mid_y))
        
        waypoints.append((mid_x, mid_y))
        waypoints.append(base_pos)
        
        return waypoints
    
    def adapt_sensor_fusion_confidence(self, sensor_health_map, weather_conditions):
        """Adjust sensor fusion confidence based on hardware health and weather."""
        confidence_adjustments = {}
        
        gps_confidence = 0.9
        if weather_conditions.get("visibility", 1.0) < 0.3:
            gps_confidence *= 0.6
        if not sensor_health_map.get("gps", True):
            gps_confidence *= 0.2
        
        imu_confidence = 0.95
        wind_speed = weather_conditions.get("wind_speed", 0.0)
        if wind_speed > 10:
            imu_confidence *= 0.8
        if not sensor_health_map.get("imu", True):
            imu_confidence *= 0.3
        
        lidar_confidence = 0.92
        if weather_conditions.get("precipitation", 0.0) > 0.6:
            lidar_confidence *= 0.5
        if not sensor_health_map.get("lidar", True):
            lidar_confidence *= 0.2
        
        return {
            "gps": max(0.0, gps_confidence),
            "imu": max(0.0, imu_confidence),
            "lidar": max(0.0, lidar_confidence),
        }
