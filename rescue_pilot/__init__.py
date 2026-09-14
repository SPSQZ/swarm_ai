"""RescuePilot: Autonomous AI Mission Commander for Search-and-Rescue Drone Swarms.

Built with the Strands Agents SDK for the 'Agents for Humans' hackathon.
"""

from rescue_pilot.tools import (
    weather_assessment_tool,
    environment_hazard_tool,
    swarm_allocation_tool,
    path_planning_tool,
    sar_investigation_tool,
    failure_recovery_tool,
    mission_report_tool,
    ALL_TOOLS,
)
from rescue_pilot.agent import RescuePilotAgent

__all__ = [
    "RescuePilotAgent",
    "weather_assessment_tool",
    "environment_hazard_tool",
    "swarm_allocation_tool",
    "path_planning_tool",
    "sar_investigation_tool",
    "failure_recovery_tool",
    "mission_report_tool",
    "ALL_TOOLS",
]
