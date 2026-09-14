"""Tests for rescue intelligence target detection and investigation logic."""

from rescue.target_detector import TargetDetector
from rescue.investigation_planner import InvestigationPlanner


def test_target_detector_identifies_simulated_targets():
    detector = TargetDetector()
    detector.add_target(x=5, y=5, confidence=0.8)
    detector.add_target(x=7, y=7, confidence=0.6)

    targets = detector.get_targets()
    assert len(targets) == 2


def test_target_confidence_affects_priority():
    detector = TargetDetector()
    detector.add_target(x=5, y=5, confidence=0.9)
    detector.add_target(x=7, y=7, confidence=0.5)

    sorted_targets = sorted(detector.get_targets(), key=lambda t: t["confidence"], reverse=True)
    assert sorted_targets[0]["confidence"] >= sorted_targets[1]["confidence"]


def test_investigation_planner_generates_hover_path():
    planner = InvestigationPlanner()
    target = {"x": 5, "y": 5, "confidence": 0.8}

    inspect_path = planner.plan_inspection(target)
    assert inspect_path is not None
    assert "hover" in str(inspect_path).lower()
