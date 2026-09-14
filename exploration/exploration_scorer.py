"""Exploration region scoring for information gain and priority."""


class ExplorationScorer:
    def __init__(self, information_weight=0.6, distance_weight=0.4):
        self.information_weight = information_weight
        self.distance_weight = distance_weight

    def score_region(self, region):
        """Score a region based on unknown cell count and other factors."""
        unknown_count = region.get("unknown_count", 0)
        distance = region.get("distance", 1.0)

        information_score = min(1.0, unknown_count / 20.0)
        distance_score = min(1.0, 1.0 / (distance + 1.0))

        total_score = (
            self.information_weight * information_score
            + self.distance_weight * distance_score
        )

        return total_score
