"""Tests for scenario runner and evaluation framework."""

from evaluation.scenario_runner import ScenarioRunner
from evaluation.metrics_collector import MetricsCollector
from evaluation.evaluation_framework import EvaluationFramework


def test_scenario_runner_executes_scenario():
    runner = ScenarioRunner()
    scenario = {
        "name": "simple_navigation",
        "num_drones": 1,
        "world_size": (50, 50),
        "start_position": (0, 0),
        "goal_position": (10, 10),
    }
    
    result = runner.run_scenario(scenario)
    assert result is not None
    assert "completion" in result


def test_metrics_collector_tracks_distance():
    collector = MetricsCollector()
    
    collector.record_position(drone_id=1, x=0, y=0, z=0)
    collector.record_position(drone_id=1, x=1, y=1, z=0)
    collector.record_position(drone_id=1, x=2, y=2, z=0)
    
    distance = collector.get_total_distance(drone_id=1)
    assert distance > 0


def test_evaluation_framework_generates_report():
    framework = EvaluationFramework()
    
    test_results = {
        "navigation": {"success": True, "time": 10.0},
        "obstacle_avoidance": {"collisions": 0},
        "energy": {"battery_used": 20},
    }
    
    report = framework.generate_report(test_results)
    assert report is not None
    assert "summary" in report


def test_metrics_collector_calculates_coverage():
    collector = MetricsCollector()
    
    for x in range(10):
        for y in range(10):
            collector.mark_cell_visited(x, y)
    
    coverage = collector.get_coverage_percentage()
    assert coverage > 0


def test_evaluation_framework_compares_scenarios():
    framework = EvaluationFramework()
    
    results_1 = {"time": 15.0, "energy": 30, "success": True}
    results_2 = {"time": 10.0, "energy": 25, "success": True}
    
    comparison = framework.compare_results([results_1, results_2])
    assert comparison is not None
