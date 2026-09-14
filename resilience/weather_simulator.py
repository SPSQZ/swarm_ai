"""Weather simulation including wind, storms, and visibility degradation."""

import random


class WeatherSimulator:
    def __init__(self):
        self.storm_intensity = 0.0
        self.wind_direction = 0.0
        self.base_wind_speed = 0.0
        self.visibility = 1.0
        self.precipitation = 0.0
    
    def set_storm_intensity(self, intensity):
        """Set storm intensity from 0.0 (calm) to 1.0 (severe)."""
        self.storm_intensity = max(0.0, min(1.0, intensity))
        self.visibility = 1.0 - (self.storm_intensity * 0.7)
        self.precipitation = self.storm_intensity * 0.8
    
    def generate_wind_gust(self):
        """Generate a wind gust based on current storm intensity."""
        base_speed = 2.0 + (self.storm_intensity * 18.0)
        gust_variation = random.uniform(-2.0, 3.0)
        speed = max(0.0, base_speed + gust_variation)
        
        direction = self.wind_direction + random.uniform(-15, 15)
        direction = direction % 360
        
        return {
            "speed": speed,
            "direction": direction,
            "intensity": self.storm_intensity,
            "gusting": speed > (base_speed + 2.0),
        }
    
    def get_visibility(self):
        """Return current visibility as a value from 0.0 to 1.0."""
        dust_factor = self.precipitation * 0.5
        visibility = self.visibility - dust_factor
        return max(0.0, min(1.0, visibility))
    
    def update_weather(self, time_step=1.0):
        """Update weather conditions over time."""
        intensity_change = random.uniform(-0.05, 0.08)
        self.storm_intensity = max(0.0, min(1.0, self.storm_intensity + intensity_change))
        self.visibility = 1.0 - (self.storm_intensity * 0.7)
        self.wind_direction += random.uniform(-5, 5)
        self.wind_direction = self.wind_direction % 360
    
    def is_safe_for_flight(self, max_wind_speed=15.0, min_visibility=0.2):
        """Check if current weather conditions are safe for flight."""
        wind = self.generate_wind_gust()
        return wind["speed"] <= max_wind_speed and self.get_visibility() >= min_visibility
