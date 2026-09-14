"""Tests for storm and terrain resilience."""

from resilience.weather_simulator import WeatherSimulator
from resilience.terrain_risk_assessor import TerrainRiskAssessor
from resilience.adaptive_controller import AdaptiveController


def test_weather_simulator_generates_wind():
    weather = WeatherSimulator()
    wind = weather.generate_wind_gust()
    
    assert wind is not None
    assert "speed" in wind
    assert "direction" in wind
    assert wind["speed"] >= 0


def test_weather_simulator_generates_visibility_conditions():
    weather = WeatherSimulator()
    weather.set_storm_intensity(0.7)
    visibility = weather.get_visibility()
    
    assert isinstance(visibility, float)
    assert 0.0 <= visibility <= 1.0


def test_terrain_risk_assessor_calculates_exposure():
    assessor = TerrainRiskAssessor()
    
    risk_low = assessor.calculate_terrain_risk(slope=0.1, roughness=0.2, exposure=0.3)
    risk_high = assessor.calculate_terrain_risk(slope=0.8, roughness=0.9, exposure=0.95)
    
    assert risk_low < risk_high
    assert 0.0 <= risk_low <= 1.0
    assert 0.0 <= risk_high <= 1.0


def test_adaptive_controller_modifies_speed_for_weather():
    controller = AdaptiveController()
    
    normal_speed = controller.calculate_safe_speed(wind_speed=2.0, visibility=1.0)
    storm_speed = controller.calculate_safe_speed(wind_speed=15.0, visibility=0.3)
    
    assert normal_speed > storm_speed


def test_adaptive_controller_contracts_formation_under_risk():
    controller = AdaptiveController()
    
    formation_normal = controller.adapt_formation_spacing(
        base_spacing=2.0,
        weather_risk=0.2,
        terrain_risk=0.1
    )
    
    formation_risky = controller.adapt_formation_spacing(
        base_spacing=2.0,
        weather_risk=0.8,
        terrain_risk=0.9
    )
    
    assert formation_risky < formation_normal


def test_adaptive_controller_triggers_emergency_hold():
    controller = AdaptiveController()
    
    should_hold = controller.should_trigger_emergency_hold(
        wind_speed=20.0,
        visibility=0.1,
        battery_level=50.0
    )
    
    assert should_hold is True
