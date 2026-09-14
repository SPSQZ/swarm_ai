"""Path selection logic for choosing the best trajectory from candidates."""


class PathSelector:
    def __init__(self, cost_function):
        self.cost_function = cost_function

    def select_best(self, candidates, goal, environment=None):
        """Choose the lowest-cost trajectory from a list of candidates."""
        if not candidates:
            return None

        best_trajectory = None
        best_cost = float("inf")

        for candidate in candidates:
            cost = self.cost_function.calculate_cost(candidate, goal, environment)
            if cost < best_cost:
                best_cost = cost
                best_trajectory = candidate

        return best_trajectory

    def select_top_n(self, candidates, goal, n=3, environment=None):
        """Return the top-n lowest-cost trajectories."""
        scored = [
            (candidate, self.cost_function.calculate_cost(candidate, goal, environment))
            for candidate in candidates
        ]
        scored.sort(key=lambda x: x[1])
        return [traj for traj, cost in scored[:n]]
