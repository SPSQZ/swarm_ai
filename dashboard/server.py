"""HTTP Simulation Server and REST API for the Drone Mission Dashboard.

Serves the interactive 2D/3D visual mission dashboard and exposes REST endpoints
for real-time swarm telemetry, dynamic formation switching, weather injection,
scenario loading, and QGroundControl/MAVLink export.
"""

import http.server
import json
import math
import os
import socketserver
import sys
import urllib.parse
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from environment.obstacles import Obstacle, distance_to_obstacle, is_in_no_go_zone
from environment.terrain import Environment, TerrainCell
from interfaces.mavlink_bridge import MAVLinkBridge
from planner.generator import PathGenerator
from rescue.target_detector import TargetDetector
from rescue_pilot.agent import RescuePilotAgent
from rescue_pilot.mission_events import MissionEventManager
from resilience.adaptive_controller import AdaptiveController
from resilience.weather_simulator import WeatherSimulator
from simulation.world import World
from swarm.formation import FormationController
from swarm.intelligent_formation import IntelligentFormationPlanner


class MissionSimulationEngine:
    """Live simulation state and update engine for the dashboard."""

    def __init__(self, width: float = 120.0, height: float = 120.0):
        self.width = width
        self.height = height
        self.running = True
        self.time = 0.0
        self.dt = 0.1
        self.speed_multiplier = 1.0

        # Subsystems
        self.world = World(width=width, height=height)
        self.weather = WeatherSimulator()
        self.weather.set_storm_intensity(0.15)
        self.wind_speed = 4.5
        self.wind_dir = 45.0
        self.adaptive_ctrl = AdaptiveController()
        self.formation_ctrl = FormationController(formation_type="wedge", spacing=6.0)
        self.intelligent_planner = IntelligentFormationPlanner()
        self.mavlink_bridge = MAVLinkBridge(origin_lat=47.397742, origin_lon=8.545594)

        # RescuePilot Strands Agent & Closed-Loop Observation
        self.agent = RescuePilotAgent()
        self.event_mgr = MissionEventManager(agent=self.agent)

        # Swarm State
        self.formation_type = "wedge"
        self.auto_formation = True
        self.drones: List[Dict[str, Any]] = []
        self.current_waypoints: List[List[float]] = []
        self.waypoint_index = 0

        # Targets (SAR)
        self.targets: List[Dict[str, Any]] = []

        # Metrics
        self.metrics = {
            "total_distance": 0.0,
            "coverage_pct": 0.0,
            "visited_cells": set(),
            "collisions": 0,
            "active_failures": [],
        }

        # Initialize Default Mission
        self.load_scenario("search_and_rescue")

    def load_scenario(self, scenario_type: str = "search_and_rescue"):
        """Initialize simulation with a specific scenario setup."""
        self.time = 0.0
        self.metrics["total_distance"] = 0.0
        self.metrics["visited_cells"].clear()
        self.metrics["collisions"] = 0
        self.metrics["active_failures"].clear()

        # Build flight path waypoints
        gen = PathGenerator()
        if scenario_type == "obstacle_course":
            traj = gen.generate_turn(start=(15.0, 15.0), goal=(105.0, 105.0), altitude=12.0)
            self.current_waypoints = traj.points + [(105.0, 30.0), (30.0, 90.0)]
        elif scenario_type == "storm_resilience":
            traj = gen.generate_straight(start=(10.0, 20.0), goal=(110.0, 100.0), altitude=10.0)
            self.current_waypoints = traj.points + [(110.0, 20.0), (10.0, 10.0)]
            self.weather.set_storm_intensity(0.8)
            self.wind_speed = 14.0
        else:  # Search and Rescue default
            traj = gen.generate_turn(start=(15.0, 20.0), goal=(95.0, 85.0), altitude=14.0)
            self.current_waypoints = [(15.0, 20.0), (45.0, 35.0), (80.0, 50.0), (100.0, 90.0), (50.0, 100.0), (20.0, 60.0)]

        self.waypoint_index = 0

        # Spawn 4 Drones
        self.drones = [
            {"id": 1, "name": "Alpha (Lead)", "x": 15.0, "y": 20.0, "z": 12.0, "vx": 0.0, "vy": 0.0, "vz": 0.0, "battery": 98.0, "mode": "LEAD", "status": "nominal"},
            {"id": 2, "name": "Bravo", "x": 10.0, "y": 15.0, "z": 12.0, "vx": 0.0, "vy": 0.0, "vz": 0.0, "battery": 95.0, "mode": "WING_L", "status": "nominal"},
            {"id": 3, "name": "Charlie", "x": 10.0, "y": 25.0, "z": 12.0, "vx": 0.0, "vy": 0.0, "vz": 0.0, "battery": 94.0, "mode": "WING_R", "status": "nominal"},
            {"id": 4, "name": "Delta", "x": 5.0, "y": 20.0, "z": 12.0, "vx": 0.0, "vy": 0.0, "vz": 0.0, "battery": 92.0, "mode": "TAIL", "status": "nominal"},
        ]

        # Targets to discover
        self.targets = [
            {"id": 1, "type": "Hiker / Survivor", "x": 55.0, "y": 42.0, "z": 0.0, "confidence": 0.94, "status": "investigated"},
            {"id": 2, "type": "Emergency Beacon", "x": 88.0, "y": 78.0, "z": 0.0, "confidence": 0.82, "status": "detected"},
            {"id": 3, "type": "Vehicle Wreckage", "x": 35.0, "y": 92.0, "z": 0.0, "confidence": 0.75, "status": "unconfirmed"},
        ]

    def step(self):
        """Advance the simulation by dt."""
        if not self.running or not self.current_waypoints:
            return

        effective_dt = self.dt * self.speed_multiplier
        self.time += effective_dt

        # Weather update
        self.weather.update_weather(effective_dt)
        gust = self.weather.generate_wind_gust()
        wind_speed = gust["speed"]
        wind_dir = gust["direction"]
        self.wind_speed = wind_speed
        self.wind_dir = wind_dir
        vis = self.weather.get_visibility()

        # Lead drone target waypoint
        target_pt = self.current_waypoints[self.waypoint_index]
        lead = self.drones[0]

        dx = target_pt[0] - lead["x"]
        dy = target_pt[1] - lead["y"]
        dist = math.hypot(dx, dy)

        if dist < 4.0:
            # Advance to next waypoint or loop
            self.waypoint_index = (self.waypoint_index + 1) % len(self.current_waypoints)
            target_pt = self.current_waypoints[self.waypoint_index]
            dx = target_pt[0] - lead["x"]
            dy = target_pt[1] - lead["y"]
            dist = max(1e-3, math.hypot(dx, dy))

        # Cruise speed with weather adaptation
        target_speed = self.adaptive_ctrl.calculate_safe_speed(
            wind_speed=wind_speed,
            visibility=vis,
            base_speed=4.5,
        )

        # Lead velocity
        lead_vx = (dx / dist) * target_speed
        lead_vy = (dy / dist) * target_speed
        lead["vx"] = lead_vx
        lead["vy"] = lead_vy
        lead["x"] += lead_vx * effective_dt
        lead["y"] += lead_vy * effective_dt
        lead["battery"] = max(0.0, lead["battery"] - 0.02 * effective_dt)

        self.metrics["total_distance"] += target_speed * effective_dt
        self.metrics["visited_cells"].add((int(lead["x"] / 5.0), int(lead["y"] / 5.0)))

        # Dynamic formation selection
        if self.auto_formation:
            formation_opt = self.intelligent_planner.select_formation({
                "mission_type": "rescue",
                "wind_speed": wind_speed,
                "energy_available": lead["battery"],
                "terrain_difficulty": 0.4,
            })
            self.formation_type = formation_opt.get("type", "wedge")
            spacing = self.adaptive_ctrl.adapt_formation_spacing(
                base_spacing=6.0,
                weather_risk=min(1.0, wind_speed / 15.0),
                terrain_risk=0.3,
            )
            self.formation_ctrl.formation_type = self.formation_type
            self.formation_ctrl.spacing = spacing

        offsets = self.formation_ctrl.get_formation_offsets(num_drones=len(self.drones))

        # Follower drone dynamics
        heading = math.atan2(lead_vy, lead_vx) if (lead_vx != 0 or lead_vy != 0) else 0.0
        cos_h = math.cos(heading)
        sin_h = math.sin(heading)

        for i, drone in enumerate(self.drones[1:], start=1):
            if i < len(offsets):
                off_x, off_y = offsets[i]
                # Rotate offset into heading frame
                target_x = lead["x"] - off_x * cos_h + off_y * sin_h
                target_y = lead["y"] - off_x * sin_h - off_y * cos_h

                f_dx = target_x - drone["x"]
                f_dy = target_y - drone["y"]
                f_dist = math.hypot(f_dx, f_dy)

                follow_speed = min(6.0, f_dist * 2.0)
                if f_dist > 0.1:
                    drone["vx"] = (f_dx / f_dist) * follow_speed
                    drone["vy"] = (f_dy / f_dist) * follow_speed
                else:
                    drone["vx"] = 0.0
                    drone["vy"] = 0.0

                drone["x"] += drone["vx"] * effective_dt
                drone["y"] += drone["vy"] * effective_dt
                drone["battery"] = max(0.0, drone["battery"] - 0.018 * effective_dt)
                self.metrics["visited_cells"].add((int(drone["x"] / 5.0), int(drone["y"] / 5.0)))

        # Update coverage
        total_cells = (self.width / 5.0) * (self.height / 5.0)
        self.metrics["coverage_pct"] = round(min(100.0, (len(self.metrics["visited_cells"]) / max(1, total_cells)) * 100.0), 1)

        # Closed-loop telemetry observation & autonomous agent replanning
        self.event_mgr.check_telemetry_and_replan(self)

    def get_state(self) -> Dict[str, Any]:
        """Return full JSON-serializable snapshot of simulation."""
        wind_speed = self.wind_speed
        wind_dir = self.wind_dir

        # Obstacles from world
        obstacles = [
            {"x": obs.x, "y": obs.y, "radius": obs.radius, "height": obs.height}
            for obs in self.world.static_obstacles
        ]
        if not obstacles:
            # Default rich obstacle field if empty
            obstacles = [
                {"x": 35.0, "y": 30.0, "radius": 6.0, "height": 25.0},
                {"x": 65.0, "y": 60.0, "radius": 8.0, "height": 30.0},
                {"x": 85.0, "y": 35.0, "radius": 5.0, "height": 18.0},
                {"x": 30.0, "y": 80.0, "radius": 7.0, "height": 22.0},
            ]

        no_go_zones = [
            {"x1": 50.0, "y1": 10.0, "x2": 65.0, "y2": 25.0, "label": "Restricted Airspace"},
            {"x1": 80.0, "y1": 85.0, "x2": 105.0, "y2": 105.0, "label": "Hazardous Mountain Peak"},
        ]

        return {
            "running": self.running,
            "time": round(self.time, 1),
            "world": {"width": self.width, "height": self.height},
            "drones": self.drones,
            "formation": {
                "type": self.formation_type,
                "spacing": round(self.formation_ctrl.spacing, 1),
                "auto": self.auto_formation,
            },
            "weather": {
                "wind_speed": round(wind_speed, 1),
                "wind_dir": round(wind_dir, 0),
                "visibility": round(self.weather.visibility, 2),
                "storm": wind_speed > 9.0,
            },
            "obstacles": obstacles,
            "no_go_zones": no_go_zones,
            "targets": self.targets,
            "waypoints": self.current_waypoints,
            "waypoint_index": self.waypoint_index,
            "metrics": {
                "total_distance": round(self.metrics["total_distance"], 1),
                "coverage_pct": self.metrics["coverage_pct"],
                "collisions": self.metrics["collisions"],
                "active_failures": self.metrics["active_failures"],
            },
            "agent": {
                "mission_state": self.agent.mission_state,
                "recent_trace": self.agent.get_trace()[-12:],
            },
        }

    def execute_command(self, cmd: Dict[str, Any]) -> Dict[str, Any]:
        """Process command received from dashboard."""
        action = cmd.get("action", "")

        if action == "play":
            self.running = True
        elif action == "pause":
            self.running = False
        elif action == "toggle_play":
            self.running = not self.running
        elif action == "reset":
            self.load_scenario("search_and_rescue")
        elif action == "set_formation":
            f_type = cmd.get("formation", "wedge").lower()
            self.formation_type = f_type
            self.formation_ctrl.formation_type = f_type
            self.auto_formation = cmd.get("auto", False)
            if "spacing" in cmd:
                self.formation_ctrl.spacing = float(cmd["spacing"])
        elif action == "inject_weather":
            speed = float(cmd.get("wind_speed", 10.0))
            is_storm = bool(cmd.get("storm", False))
            self.wind_speed = speed
            self.weather.set_storm_intensity(0.85 if is_storm else min(1.0, speed / 20.0))
        elif action == "inject_failure":
            fail_type = cmd.get("type", "gps_loss")
            drone_id = int(cmd.get("drone_id", 2))
            for d in self.drones:
                if d["id"] == drone_id:
                    d["status"] = fail_type
            if fail_type not in self.metrics["active_failures"]:
                self.metrics["active_failures"].append(fail_type)
        elif action == "load_scenario":
            scenario_name = cmd.get("scenario", "search_and_rescue")
            self.load_scenario(scenario_name)

        return {"status": "ok", "action": action}


# Global Simulation Instance
SIMULATION = MissionSimulationEngine()


class DashboardHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving the visual dashboard and JSON API."""

    def __init__(self, *args, **kwargs):
        dashboard_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=dashboard_dir, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/state":
            SIMULATION.step()
            state = SIMULATION.get_state()
            self._send_json(state)
        elif parsed.path == "/api/agent/trace":
            self._send_json({
                "trace": SIMULATION.agent.get_trace(),
                "mission_state": SIMULATION.agent.mission_state,
            })
        elif parsed.path == "/api/agent/sitrep":
            sitrep = SIMULATION.agent.generate_sitrep()
            self._send_json(sitrep)
        elif parsed.path == "/api/export/qgc_plan":
            pts = SIMULATION.current_waypoints
            plan = SIMULATION.mavlink_bridge.export_qgroundcontrol_plan(pts)
            self._send_download(json.dumps(plan, indent=2), "mission.plan", "application/json")
        elif parsed.path == "/api/export/waypoints":
            pts = SIMULATION.current_waypoints
            wpl = SIMULATION.mavlink_bridge.export_wpl_waypoints(pts)
            self._send_download(wpl, "mission.waypoints", "text/plain")
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/agent/command":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8")
            try:
                data = json.loads(body) if body else {}
            except Exception:
                data = {}
            prompt = data.get("prompt", "")
            res = SIMULATION.agent.execute_command(prompt)

            # Apply Agent Decisions directly to physical Swarm Simulation
            if "path" in res and "waypoints" in res["path"]:
                new_wps = [[p[0], p[1]] for p in res["path"]["waypoints"]]
                if new_wps:
                    SIMULATION.current_waypoints = new_wps
                    SIMULATION.waypoint_index = 0
            if "swarm" in res:
                SIMULATION.formation_type = res["swarm"]["formation_type"]
                SIMULATION.formation_ctrl.formation_type = SIMULATION.formation_type
                SIMULATION.formation_ctrl.spacing = res["swarm"]["inter_drone_spacing_m"]
            if "weather" in res:
                w = res["weather"]
                SIMULATION.wind_speed = w["wind_speed_ms"]
                if w.get("storm_active"):
                    SIMULATION.weather.set_storm_intensity(0.85)

            self._send_json(res)
        elif parsed.path == "/api/agent/trigger_event":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8")
            try:
                data = json.loads(body) if body else {}
            except Exception:
                data = {}
            ev_type = data.get("event_type", "WEATHER_ALERT")
            ev_data = data.get("data", {})
            res = SIMULATION.event_mgr.trigger_manual_event(ev_type, ev_data, SIMULATION)
            self._send_json(res)
        elif parsed.path == "/api/command":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8")
            try:
                cmd = json.loads(body) if body else {}
            except Exception:
                cmd = {}

            res = SIMULATION.execute_command(cmd)
            self._send_json(res)
        elif parsed.path == "/api/step":
            SIMULATION.step()
            self._send_json({"status": "ok", "time": SIMULATION.time})
        else:
            self.send_error(404, "Endpoint not found")

    def _send_json(self, data: Any):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_download(self, text_data: str, filename: str, content_type: str):
        payload = text_data.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        """Suppress standard access logs for cleaner console output."""
        return


def run_dashboard_server(port: int = 8080, bind: str = "127.0.0.1") -> socketserver.TCPServer:
    """Start the dashboard HTTP server."""
    current_port = port
    for _ in range(10):
        try:
            server = socketserver.TCPServer((bind, current_port), DashboardHTTPHandler)
            return server, current_port
        except OSError:
            current_port += 1

    raise RuntimeError("Could not find an available port to bind dashboard server.")


if __name__ == "__main__":
    server, port = run_dashboard_server()
    print(f"🚀 Drone Mission Dashboard live at: http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard server stopped.")
        server.server_close()
