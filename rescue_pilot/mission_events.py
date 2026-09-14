"""Closed-Loop Mission Event Manager for Dynamic Telemetry Observation & Replanning.

Monitors real-time swarm physics, weather spikes, survivor discoveries, and drone failures,
automatically routing environmental triggers to the Strands Agent for autonomous replanning.
"""

from typing import Any, Dict, List, Optional
import math
import time

from rescue_pilot.agent import RescuePilotAgent


class MissionEventManager:
    """Monitors live simulation state and triggers closed-loop Strands agent replanning."""

    def __init__(self, agent: Optional[RescuePilotAgent] = None):
        self.agent = agent or RescuePilotAgent()
        self.handled_events: set = set()
        self.last_weather_alert_time = 0.0
        self.last_check_time = 0.0

    def check_telemetry_and_replan(self, simulation_engine: Any) -> Optional[Dict[str, Any]]:
        """Evaluate real-time simulation state and trigger Strands Agent if conditions require.

        Args:
            simulation_engine: The active MissionSimulationEngine instance.

        Returns:
            Dict describing the replan action if an event was handled, or None.
        """
        now = simulation_engine.time

        # Check 1: Severe Weather Spike Trigger
        wind_speed = getattr(simulation_engine, "wind_speed", 5.0)
        is_storm = getattr(simulation_engine, "weather", None) and getattr(simulation_engine.weather, "storm_intensity", 0.0) > 0.6
        if (wind_speed >= 11.5 or is_storm) and (now - self.last_weather_alert_time > 15.0):
            event_key = f"weather_{int(now / 15.0)}"
            if event_key not in self.handled_events:
                self.handled_events.add(event_key)
                self.last_weather_alert_time = now
                replan_result = self.agent.handle_event(
                    "WEATHER_ALERT",
                    {"wind_speed": wind_speed, "storm_active": True, "time": now}
                )
                # Apply replan to simulation
                simulation_engine.formation_type = replan_result.get("formation", "wedge")
                simulation_engine.formation_ctrl.formation_type = simulation_engine.formation_type
                simulation_engine.formation_ctrl.spacing = replan_result.get("spacing", 4.5)
                return replan_result

        # Check 2: Target / Survivor Proximity Trigger
        drones = getattr(simulation_engine, "drones", [])
        targets = getattr(simulation_engine, "targets", [])
        for target in targets:
            target_id = target.get("id", 0)
            if target.get("status") == "unconfirmed" or target.get("status") == "detected":
                for drone in drones:
                    dist = math.hypot(drone["x"] - target["x"], drone["y"] - target["y"])
                    if dist < 16.0:  # Sensor detection cone
                        event_key = f"target_{target_id}"
                        if event_key not in self.handled_events:
                            self.handled_events.add(event_key)
                            target["status"] = "investigated"
                            replan_result = self.agent.handle_event(
                                "SURVIVOR_DETECTED",
                                {
                                    "target_id": target_id,
                                    "target_type": target.get("type", "Survivor"),
                                    "coords": [target["x"], target["y"]],
                                    "confidence": target.get("confidence", 0.94),
                                    "detecting_drone_id": drone["id"],
                                }
                            )
                            # Temporarily adjust waypoints to hover around target
                            curr_pts = simulation_engine.current_waypoints
                            insert_pt = [target["x"], target["y"]]
                            if insert_pt not in curr_pts:
                                simulation_engine.current_waypoints.insert(
                                    (simulation_engine.waypoint_index + 1) % max(1, len(curr_pts)),
                                    insert_pt,
                                )
                            return replan_result

        # Check 3: Active Drone Failures (Honest Degradation)
        active_fails = simulation_engine.metrics.get("active_failures", [])
        for fail_type in active_fails:
            event_key = f"fail_{fail_type}"
            if event_key not in self.handled_events:
                self.handled_events.add(event_key)
                # Find which drone failed
                failing_drone = next((d for d in drones if d["status"] == fail_type), drones[-1] if drones else None)
                fail_id = failing_drone["id"] if failing_drone else 3
                replan_result = self.agent.handle_event(
                    "DRONE_FAILURE",
                    {"drone_id": fail_id, "failure_type": fail_type}
                )
                # Apply rebalanced formation and spacing to simulation
                simulation_engine.formation_type = replan_result.get("new_formation", "wedge")
                simulation_engine.formation_ctrl.formation_type = simulation_engine.formation_type
                simulation_engine.formation_ctrl.spacing = replan_result.get("new_spacing", 6.5)
                return replan_result

        return None

    def trigger_manual_event(self, event_type: str, event_data: Dict[str, Any], simulation_engine: Any) -> Dict[str, Any]:
        """Manually inject an emergency event (from dashboard controls) for demonstration."""
        replan_res = self.agent.handle_event(event_type, event_data)

        if event_type == "WEATHER_ALERT":
            speed = float(event_data.get("wind_speed", 14.0))
            simulation_engine.wind_speed = speed
            if hasattr(simulation_engine, "weather"):
                simulation_engine.weather.set_storm_intensity(0.85)
            simulation_engine.formation_type = replan_res.get("formation", "wedge")
            simulation_engine.formation_ctrl.formation_type = simulation_engine.formation_type
            simulation_engine.formation_ctrl.spacing = replan_res.get("spacing", 4.5)

        elif event_type == "DRONE_FAILURE":
            drone_id = int(event_data.get("drone_id", 3))
            fail_type = event_data.get("failure_type", "gps_loss")
            for d in simulation_engine.drones:
                if d["id"] == drone_id:
                    d["status"] = fail_type
            if fail_type not in simulation_engine.metrics["active_failures"]:
                simulation_engine.metrics["active_failures"].append(fail_type)
            simulation_engine.formation_type = replan_res.get("new_formation", "wedge")
            simulation_engine.formation_ctrl.formation_type = simulation_engine.formation_type
            simulation_engine.formation_ctrl.spacing = replan_res.get("new_spacing", 6.5)

        elif event_type == "SURVIVOR_DETECTED":
            coords = event_data.get("coords", [55.0, 42.0])
            for t in simulation_engine.targets:
                if abs(t["x"] - coords[0]) < 5.0 and abs(t["y"] - coords[1]) < 5.0:
                    t["status"] = "investigated"
            # Insert hover waypoint
            simulation_engine.current_waypoints.insert(
                (simulation_engine.waypoint_index + 1) % max(1, len(simulation_engine.current_waypoints)),
                coords,
            )

        return replan_res
