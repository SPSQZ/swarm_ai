"""Base sensor interface for simulated drone sensors."""


class Sensor:
    def __init__(self, name: str, noise: float = 0.0, confidence: float = 1.0):
        self.name = name
        self.noise = noise
        self.confidence = confidence
        self.value = 0.0
        self.is_healthy = True
        self.is_missing = False

    def read(self):
        if self.is_missing or not self.is_healthy:
            return None
        return round(self.value, 2)

    def update(self, value):
        if self.is_missing or not self.is_healthy:
            return
        self.value = round(value + self.noise, 2)

    def set_missing(self, missing: bool):
        self.is_missing = missing

    def fail(self):
        self.is_healthy = False
        self.confidence = 0.0

    def recover(self):
        self.is_healthy = True
        self.confidence = max(0.0, min(1.0, self.confidence if self.confidence > 0 else 1.0))
