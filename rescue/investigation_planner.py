"""Investigation planning for target inspection and confirmation."""


class InvestigationPlanner:
    def __init__(self, inspect_altitude=5.0, inspect_hover_time=10.0):
        self.inspect_altitude = inspect_altitude
        self.inspect_hover_time = inspect_hover_time

    def plan_inspection(self, target, current_position=(0, 0)):
        """Generate an inspection path: move to target and hover for observation."""
        target_x = target.get("x", 0)
        target_y = target.get("y", 0)

        inspection_plan = {
            "target_id": target.get("id", None),
            "destination": (target_x, target_y),
            "altitude": self.inspect_altitude,
            "actions": ["move_to_target", "hover_and_inspect", "confirm_or_dismiss"],
            "hover_time": self.inspect_hover_time,
            "confidence": target.get("confidence", 0.5),
        }

        return inspection_plan

    def generate_inspection_sequence(self, targets):
        """Create an inspection sequence for multiple high-priority targets."""
        sequence = []
        for target in targets:
            plan = self.plan_inspection(target)
            sequence.append(plan)
        return sequence
