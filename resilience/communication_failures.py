"""Communication failure simulation for multi-drone scenarios."""

import random
from datetime import datetime, timedelta


class CommunicationFailureManager:
    def __init__(self):
        self.packet_loss_rate = 0.0
        self.link_outages = {}
        self.latency_ms = 0
        self.bandwidth_degradation = 1.0
    
    def set_packet_loss_rate(self, rate):
        """Set the probability of packet loss (0.0 to 1.0)."""
        self.packet_loss_rate = max(0.0, min(1.0, rate))
    
    def should_drop_packet(self):
        """Determine if a packet should be dropped based on loss rate."""
        return random.random() < self.packet_loss_rate
    
    def simulate_link_outage(self, drone_id, duration=10):
        """Simulate a communication link outage for a drone."""
        self.link_outages[drone_id] = {
            "outage_start": datetime.now(),
            "duration": duration,
            "active": True,
        }
    
    def is_drone_connected(self, drone_id):
        """Check if a drone's communication link is active."""
        if drone_id not in self.link_outages:
            return True
        
        outage = self.link_outages[drone_id]
        if not outage["active"]:
            return True
        
        elapsed = (datetime.now() - outage["outage_start"]).total_seconds()
        if elapsed >= outage["duration"]:
            outage["active"] = False
            return True
        
        return False
    
    def set_latency(self, latency_ms):
        """Set communication latency in milliseconds."""
        self.latency_ms = max(0, latency_ms)
    
    def set_bandwidth_degradation(self, degradation_factor):
        """Set bandwidth degradation factor (0.0 to 1.0)."""
        self.bandwidth_degradation = max(0.0, min(1.0, degradation_factor))
    
    def get_effective_bandwidth(self, base_bandwidth=10.0):
        """Calculate effective bandwidth after degradation."""
        return base_bandwidth * self.bandwidth_degradation
    
    def simulate_message_corruption(self, message):
        """Simulate bit flips or message corruption."""
        if random.random() < self.packet_loss_rate * 0.5:
            if isinstance(message, dict):
                corrupted = message.copy()
                for key in corrupted:
                    if isinstance(corrupted[key], float):
                        corrupted[key] *= (1.0 + random.uniform(-0.1, 0.1))
                return corrupted
        return message
    
    def get_connection_quality(self, drone_id):
        """Get quality metric (0.0 to 1.0) of connection."""
        if not self.is_drone_connected(drone_id):
            return 0.0
        
        quality = 1.0 - self.packet_loss_rate
        quality *= self.bandwidth_degradation
        
        if self.latency_ms > 0:
            latency_penalty = min(0.5, self.latency_ms / 1000.0)
            quality *= (1.0 - latency_penalty)
        
        return max(0.0, quality)
