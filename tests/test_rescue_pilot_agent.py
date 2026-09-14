"""Automated Test Suite for RescuePilot Strands Agent and Domain Tools.

Validates tool execution, agent multi-step reasoning, closed-loop event observation,
honest degradation fault tolerance, and MAVLink/QGC mission exports.
"""

import pytest
from rescue_pilot import (
    RescuePilotAgent,
    ALL_TOOLS,
    weather_assessment_tool,
    environment_hazard_tool,
    swarm_allocation_tool,
    path_planning_tool,
    sar_investigation_tool,
    failure_recovery_tool,
    mission_report_tool,
)
from rescue_pilot.mission_events import MissionEventManager


def test_tools_count_and_interface():
    """Verify all 7 specialized tools are loaded and wrapped with Strands @tool."""
    assert len(ALL_TOOLS) == 7
    expected_names = {
        "weather_assessment_tool",
        "environment_hazard_tool",
        "swarm_allocation_tool",
        "path_planning_tool",
        "sar_investigation_tool",
        "failure_recovery_tool",
        "mission_report_tool",
    }
    actual_names = {t.tool_name for t in ALL_TOOLS}
    assert actual_names == expected_names


def test_weather_assessment_tool():
    """Test atmospheric risk calculation and formation recommendation."""
    # Calm conditions
    calm = weather_assessment_tool(region="northern", current_wind=4.0, storm_forecast=False)
    assert calm["risk_level"] == "NOMINAL"
    assert calm["recommended_formation"] == "line"

    # Severe storm conditions
    storm = weather_assessment_tool(region="northern", current_wind=14.0, storm_forecast=True)
    assert storm["risk_level"] == "CRITICAL_STORM"
    assert storm["recommended_formation"] == "wedge"
    assert storm["max_safe_speed_ms"] <= 3.5
    assert storm["recommended_altitude_m"] <= 10.0


def test_environment_hazard_tool():
    """Test 3D terrain clearance and obstacle density queries."""
    res = environment_hazard_tool(target_sector="northern", altitude=12.0)
    assert res["clearance_status"] == "CLEAR"
    assert len(res["obstacles"]) >= 4
    assert len(res["no_go_zones"]) >= 2

    # Altitude below safe threshold
    low_alt = environment_hazard_tool(target_sector="northern", altitude=6.0)
    assert low_alt["clearance_status"] == "ALTITUDE_WARNING"


def test_swarm_allocation_tool():
    """Test multi-UAV role assignment and spacing adaptation."""
    alloc = swarm_allocation_tool(num_drones=4, mission_priority="survivor_detection", wind_speed=5.0)
    assert alloc["num_drones"] == 4
    assert len(alloc["fleet_roles"]) == 4
    assert alloc["formation_type"] in ["wedge", "line", "diamond", "arc"]
    assert alloc["inter_drone_spacing_m"] > 0


def test_path_planning_tool():
    """Test 3D kinematic waypoint generation and boundary checking."""
    plan = path_planning_tool(search_sector="northern", altitude=12.0, avoid_obstacles=True)
    assert plan["waypoint_count"] >= 5
    assert plan["total_distance_m"] > 50.0
    for pt in plan["waypoints"]:
        assert len(pt) == 3
        assert pt[2] == 12.0  # Altitude check


def test_sar_investigation_tool():
    """Test survivor triage, prioritization, and hover-inspection path synthesis."""
    # List targets
    targets_res = sar_investigation_tool(action="list_targets")
    assert targets_res["total_targets_detected"] >= 3

    # Prioritize
    prio_res = sar_investigation_tool(action="prioritize")
    assert prio_res["highest_priority"] is not None
    assert prio_res["highest_priority"]["confidence"] >= 0.8

    # Generate hover inspection
    insp_res = sar_investigation_tool(action="plan_inspection", target_id=0)
    assert "inspection_flight_plan" in insp_res
    actions = insp_res["inspection_flight_plan"]["actions"]
    assert "hover_and_scan_12s" in actions


def test_failure_recovery_honest_degradation():
    """Test 'Honest Degradation': isolating compromised UAV and rebalancing swarm."""
    # Drone #3 suffers GPS loss
    recovery = failure_recovery_tool(drone_id=3, failure_type="gps_loss")
    assert recovery["status"] == "RECOVERY_EXECUTED"
    assert recovery["compromised_drone"]["action"] == "OPTICAL_FLOW_HOVER_AND_SAFE_LAND"
    assert 3 not in recovery["remaining_active_drones"]
    assert len(recovery["remaining_active_drones"]) == 3
    assert recovery["swarm_rebalancing"]["new_formation"] == "wedge"

    # Drone #4 suffers battery critical
    batt_rec = failure_recovery_tool(drone_id=4, failure_type="battery_critical")
    assert batt_rec["compromised_drone"]["action"] == "AUTONOMOUS_RETURN_TO_BASE_RTB"


def test_mission_report_tool_mavlink_export():
    """Test generation of SITREP and export of QGroundControl .plan and MAVLink WPL."""
    report = mission_report_tool(format_type="all")
    assert "SITREP" in report["sitrep_text"]
    assert "qgc_plan_json" in report
    assert report["qgc_plan_json"]["fileType"] == "Plan"
    assert "mavlink_wpl_string" in report
    assert "QGC WPL 110" in report["mavlink_wpl_string"]


def test_rescue_pilot_agent_command_execution():
    """Test end-to-end command execution and multi-tool reasoning pipeline."""
    agent = RescuePilotAgent()
    prompt = "Deploy four drones to search the northern sector. Prioritize survivor detection. A storm is approaching."
    result = agent.execute_command(prompt)

    assert result["status"] == "success"
    assert "Roger Operator" in result["response"]
    assert result["swarm"]["formation_type"] == "wedge"
    assert len(result["path"]["waypoints"]) >= 6

    # Verify execution trace was populated
    trace = agent.get_trace()
    assert len(trace) >= 8
    event_types = [e["type"] for e in trace]
    assert "OPERATOR_INPUT" in event_types
    assert "REASONING" in event_types
    assert "TOOL_CALL" in event_types
    assert "TOOL_RESULT" in event_types
    assert "MISSION_DISPATCH" in event_types


def test_closed_loop_event_replan():
    """Test closed-loop dynamic replanning triggers."""
    agent = RescuePilotAgent()
    event_mgr = MissionEventManager(agent=agent)

    # Replan trigger on weather spike
    weather_event = agent.handle_event("WEATHER_ALERT", {"wind_speed": 15.0})
    assert weather_event["action"] == "CONTRACT_FORMATION"
    assert weather_event["formation"] == "wedge"

    # Replan trigger on survivor detection
    sar_event = agent.handle_event("SURVIVOR_DETECTED", {"target_id": 0, "coords": [55.0, 42.0]})
    assert sar_event["action"] == "DIVERSIFY_SWARM_INSPECTION"

    # Replan trigger on drone failure
    fail_event = agent.handle_event("DRONE_FAILURE", {"drone_id": 2, "failure_type": "gps_loss"})
    assert fail_event["action"] == "DEGRADE_AND_REBALANCE"
    assert agent.mission_state["drones_active"] == 3
