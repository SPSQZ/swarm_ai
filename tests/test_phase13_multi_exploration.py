"""Tests for multi-drone exploration and task allocation."""

from exploration.task_allocator import TaskAllocator
from exploration.coverage_manager import CoverageManager


def test_task_allocator_divides_exploration_area():
    allocator = TaskAllocator(grid_width=20, grid_height=20, num_drones=2)
    regions = allocator.divide_area()

    assert len(regions) == 2
    assert all(isinstance(r, dict) for r in regions)
    assert all("x_min" in r and "y_min" in r for r in regions)


def test_task_allocator_assigns_regions_to_drones():
    allocator = TaskAllocator(grid_width=20, grid_height=20, num_drones=3)
    assignments = allocator.allocate_tasks()

    assert len(assignments) == 3
    assert all(isinstance(a, dict) for a in assignments)
    assert all("drone_id" in a and "region" in a for a in assignments)


def test_coverage_manager_tracks_explored_cells():
    manager = CoverageManager(grid_width=10, grid_height=10)
    manager.mark_explored(5, 5, drone_id=1)
    manager.mark_explored(6, 5, drone_id=2)

    assert manager.get_explored_count() == 2
    assert manager.is_explored(5, 5)
    assert manager.get_drone_coverage(drone_id=1) >= 1


def test_coverage_manager_prevents_duplicate_exploration():
    manager = CoverageManager(grid_width=10, grid_height=10)
    manager.mark_explored(5, 5, drone_id=1)
    result = manager.mark_explored(5, 5, drone_id=2)

    assert result is False


def test_coverage_manager_detects_incomplete_areas():
    manager = CoverageManager(grid_width=5, grid_height=5)
    manager.mark_explored(0, 0, drone_id=1)

    assert manager.has_incomplete_areas() is True
