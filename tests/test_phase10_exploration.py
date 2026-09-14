"""Tests for autonomous exploration frontier detection and scoring."""

from exploration.frontier import FrontierDetector
from exploration.exploration_scorer import ExplorationScorer


def test_frontier_detector_identifies_unknown_regions():
    detector = FrontierDetector(grid_width=10, grid_height=10, resolution=1.0)

    detector.mark_explored(4, 5)
    detector.mark_explored(5, 4)
    detector.mark_explored(5, 5)

    unknown_cells = [(5, 6), (6, 5), (6, 6)]
    for x, y in unknown_cells:
        detector.mark_unknown(x, y)

    frontiers = detector.detect_frontiers()
    assert len(frontiers) > 0


def test_exploration_scorer_ranks_regions_by_information_gain():
    scorer = ExplorationScorer()

    region1 = {"x": 5, "y": 5, "unknown_count": 10}
    region2 = {"x": 7, "y": 7, "unknown_count": 3}

    score1 = scorer.score_region(region1)
    score2 = scorer.score_region(region2)

    assert score1 > score2


def test_incomplete_area_detection():
    detector = FrontierDetector(grid_width=10, grid_height=10, resolution=1.0)

    for x in range(3, 7):
        detector.mark_unknown(x, 5)

    incomplete = detector.has_incomplete_areas()
    assert incomplete is True
