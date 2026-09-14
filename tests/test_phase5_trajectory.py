"""Tests for the Phase 5 trajectory system."""

from planner.generator import PathGenerator, Trajectory


def test_trajectory_generation_types():
    generator = PathGenerator()
    candidates = generator.generate_candidates((0, 0), (10, 10))

    assert len(candidates) >= 4
    assert all(isinstance(item, Trajectory) for item in candidates)
    assert any(item.name == "straight" for item in candidates)
    assert any(item.name == "climb" for item in candidates)


def test_hover_trajectory_has_single_point():
    generator = PathGenerator()
    hover = generator.generate_hover((5, 5), altitude=6.0)
    assert hover.name == "hover"
    assert len(hover.points) == 1
    assert hover.altitude == 6.0
