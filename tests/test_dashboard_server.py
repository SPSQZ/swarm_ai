"""Tests for Mission Simulation Engine and Dashboard Server."""

import json
import threading
import urllib.request
from dashboard.server import MissionSimulationEngine, run_dashboard_server


def test_simulation_engine_initialization():
    engine = MissionSimulationEngine()
    assert engine.running is True
    assert len(engine.drones) == 4
    assert len(engine.targets) >= 2
    assert len(engine.current_waypoints) >= 2

    state = engine.get_state()
    assert "drones" in state
    assert "weather" in state
    assert "formation" in state
    assert "obstacles" in state
    assert "no_go_zones" in state


def test_simulation_engine_step():
    engine = MissionSimulationEngine()
    initial_dist = engine.metrics["total_distance"]
    lead_x = engine.drones[0]["x"]

    # Step simulation forward
    for _ in range(5):
        engine.step()

    assert engine.time > 0
    assert engine.metrics["total_distance"] > initial_dist
    assert engine.drones[0]["x"] != lead_x
    assert engine.drones[0]["battery"] < 100.0


def test_simulation_commands():
    engine = MissionSimulationEngine()

    # 1. Formation command
    res = engine.execute_command({"action": "set_formation", "formation": "diamond", "auto": False})
    assert res["status"] == "ok"
    assert engine.formation_type == "diamond"
    assert engine.auto_formation is False

    # 2. Weather injection
    res = engine.execute_command({"action": "inject_weather", "wind_speed": 18.0, "storm": True})
    assert res["status"] == "ok"
    assert engine.weather.visibility < 1.0

    # 3. Failure injection
    res = engine.execute_command({"action": "inject_failure", "type": "gps_loss", "drone_id": 2})
    assert res["status"] == "ok"
    drone2 = next(d for d in engine.drones if d["id"] == 2)
    assert drone2["status"] == "gps_loss"
    assert "gps_loss" in engine.metrics["active_failures"]

    # 4. Scenario load
    res = engine.execute_command({"action": "load_scenario", "scenario": "obstacle_course"})
    assert res["status"] == "ok"
    assert engine.time == 0.0


def test_dashboard_server_endpoints():
    server, port = run_dashboard_server(port=8990)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"

    try:
        # Test /api/state
        req = urllib.request.Request(f"{base_url}/api/state")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert "drones" in data
            assert len(data["drones"]) == 4

        # Test /api/command
        cmd_data = json.dumps({"action": "set_formation", "formation": "arc"}).encode("utf-8")
        cmd_req = urllib.request.Request(
            f"{base_url}/api/command",
            data=cmd_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(cmd_req, timeout=3.0) as resp:
            assert resp.status == 200
            res = json.loads(resp.read().decode("utf-8"))
            assert res["status"] == "ok"

        # Test /api/export/qgc_plan
        export_req = urllib.request.Request(f"{base_url}/api/export/qgc_plan")
        with urllib.request.urlopen(export_req, timeout=3.0) as resp:
            assert resp.status == 200
            plan = json.loads(resp.read().decode("utf-8"))
            assert plan["fileType"] == "Plan"
    finally:
        server.shutdown()
        server.server_close()
