"""Evaluation metrics for the drone exploration simulation."""


def mission_success_rate(successes: int, total: int) -> float:
    if total == 0:
        return 0.0
    return successes / total


def coverage_score(covered_cells: int, total_cells: int) -> float:
    if total_cells == 0:
        return 0.0
    return covered_cells / total_cells
