"""Tests for intelligent adaptive formation planning."""

from swarm.intelligent_formation import IntelligentFormationPlanner
from swarm.formation_advisor import FormationAdvisor


def test_intelligent_formation_planner_selects_efficient_formation():
    planner = IntelligentFormationPlanner(num_drones=4)
    
    mission_context = {
        "mission_type": "exploration",
        "energy_available": 80.0,
        "terrain_difficulty": 0.3,
        "wind_speed": 5.0,
        "num_obstacles": 2,
    }
    
    formation = planner.select_formation(mission_context)
    assert formation is not None
    assert formation["type"] in ["line", "wedge", "arc", "diamond"]


def test_formation_advisor_recommends_based_on_mission():
    advisor = FormationAdvisor()
    
    tight_formation = advisor.get_formation_for_mission(
        mission_type="rescue",
        num_drones=3,
        energy_available=100.0
    )
    assert tight_formation is not None
    
    spread_formation = advisor.get_formation_for_mission(
        mission_type="exploration",
        num_drones=3,
        energy_available=100.0
    )
    assert spread_formation is not None


def test_formation_adapts_to_wind():
    planner = IntelligentFormationPlanner(num_drones=4)
    
    low_wind = planner.adapt_formation_for_wind(wind_speed=2.0, base_formation="line")
    high_wind = planner.adapt_formation_for_wind(wind_speed=15.0, base_formation="line")
    
    assert low_wind is not None
    assert high_wind is not None
    assert low_wind != high_wind


def test_formation_optimizes_for_energy():
    planner = IntelligentFormationPlanner(num_drones=4)
    
    energy_efficient = planner.optimize_formation_for_energy(
        formation="line",
        battery_level=20.0,
        distance_to_travel=50.0
    )
    
    assert energy_efficient is not None
    assert "spacing_adjustment" in energy_efficient
