"""Tests for path selection and decision engine."""

from planner.cost_function import PathCostFunction
from planner.path_selector import PathSelector
from planner.generator import PathGenerator, Trajectory


def test_cost_function_scores_paths():
    cost_fn = PathCostFunction()
    traj = Trajectory(
        name="straight",
        points=[(0, 0), (10, 10)],
        altitude=5.0,
        speed=2.0,
    )

    cost = cost_fn.calculate_cost(traj, goal=(10, 10))
    assert cost >= 0.0
    assert cost <= 100.0


def test_path_selector_chooses_lowest_cost_path():
    cost_fn = PathCostFunction()
    selector = PathSelector(cost_function=cost_fn)

    traj1 = Trajectory(
        name="straight",
        points=[(0, 0), (10, 10)],
        altitude=5.0,
        speed=2.0,
    )
    traj2 = Trajectory(
        name="turn",
        points=[(0, 0), (5, 5), (10, 10)],
        altitude=5.0,
        speed=2.0,
    )

    best = selector.select_best([traj1, traj2], goal=(10, 10))
    assert best is not None
    assert best.name in ["straight", "turn"]


def test_empty_candidate_list_returns_none():
    cost_fn = PathCostFunction()
    selector = PathSelector(cost_function=cost_fn)
    best = selector.select_best([], goal=(10, 10))
    assert best is None
