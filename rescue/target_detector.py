"""Target detection for rescue and investigation missions."""


class TargetDetector:
    def __init__(self):
        self.targets = []
        self.detected_count = 0

    def add_target(self, x, y, confidence=0.5):
        """Register a discovered target with confidence level."""
        target = {
            "id": self.detected_count,
            "x": x,
            "y": y,
            "confidence": confidence,
            "confirmed": False,
        }
        self.targets.append(target)
        self.detected_count += 1

    def get_targets(self):
        """Return all detected targets."""
        return self.targets

    def confirm_target(self, target_id):
        """Mark a target as confirmed after investigation."""
        for target in self.targets:
            if target["id"] == target_id:
                target["confirmed"] = True
                return True
        return False

    def get_priority_targets(self, sort_by_confidence=True):
        """Return targets sorted by priority (confidence and confirmation status)."""
        sorted_targets = sorted(
            self.targets,
            key=lambda t: (t["confirmed"], t["confidence"]),
            reverse=True,
        )
        return sorted_targets
