"""Sensor failure simulation and degradation modeling."""

import random


class SensorFailureManager:
    def __init__(self):
        self.sensor_states = {
            "gps": {"healthy": True, "noise_multiplier": 1.0, "confidence": 1.0},
            "imu": {"healthy": True, "noise_multiplier": 1.0, "confidence": 1.0},
            "lidar": {"healthy": True, "noise_multiplier": 1.0, "confidence": 1.0},
            "altimeter": {"healthy": True, "noise_multiplier": 1.0, "confidence": 1.0},
            "camera": {"healthy": True, "noise_multiplier": 1.0, "confidence": 1.0},
        }
        self.base_noise = {
            "gps": 0.02,
            "imu": 0.01,
            "lidar": 0.02,
            "altimeter": 0.05,
            "camera": 0.0,
        }
    
    def simulate_gps_failure(self, failure_probability=0.1):
        """Randomly simulate GPS loss or degradation."""
        if random.random() < failure_probability:
            self.sensor_states["gps"]["healthy"] = False
            self.sensor_states["gps"]["confidence"] = 0.0
            return True
        return False
    
    def simulate_sensor_noise_increase(self, sensor_name, multiplier=2.0):
        """Increase noise for a specific sensor."""
        if sensor_name in self.sensor_states:
            self.sensor_states[sensor_name]["noise_multiplier"] = multiplier
            self.sensor_states[sensor_name]["confidence"] *= (1.0 / multiplier)
    
    def simulate_sensor_drift(self, sensor_name, drift_amount=0.05):
        """Simulate sensor bias/drift over time."""
        if sensor_name in self.sensor_states:
            self.sensor_states[sensor_name]["healthy"] = True
            self.sensor_states[sensor_name]["confidence"] *= 0.9
    
    def recover_sensor(self, sensor_name):
        """Recover a failed sensor to operational state."""
        if sensor_name in self.sensor_states:
            self.sensor_states[sensor_name]["healthy"] = True
            self.sensor_states[sensor_name]["noise_multiplier"] = 1.0
            self.sensor_states[sensor_name]["confidence"] = 1.0
            return True
        return False
    
    def is_sensor_healthy(self, sensor_name):
        """Check if a sensor is healthy."""
        return self.sensor_states.get(sensor_name, {}).get("healthy", False)
    
    def is_gps_healthy(self):
        """Check specifically if GPS is operational."""
        return self.sensor_states["gps"]["healthy"]
    
    def get_sensor_noise(self, sensor_name):
        """Get effective noise level for a sensor."""
        if sensor_name not in self.sensor_states:
            return 0.0
        
        base = self.base_noise.get(sensor_name, 0.0)
        multiplier = self.sensor_states[sensor_name]["noise_multiplier"]
        return base * multiplier
    
    def get_sensor_confidence(self, sensor_name):
        """Get confidence rating for a sensor."""
        return self.sensor_states.get(sensor_name, {}).get("confidence", 0.0)
    
    def get_all_sensor_status(self):
        """Get status of all sensors."""
        status = {}
        for sensor_name, state in self.sensor_states.items():
            status[sensor_name] = {
                "healthy": state["healthy"],
                "confidence": state["confidence"],
                "noise": self.get_sensor_noise(sensor_name),
            }
        return status
