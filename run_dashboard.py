"""One-command runner for RescuePilot Mission Control Dashboard.

RescuePilot: Autonomous AI Mission Commander for Search-and-Rescue Drone Swarms
Powered by the Strands Agents SDK.

Usage:
    python run_dashboard.py
"""

import sys
import threading
import time
import webbrowser
from dashboard.server import run_dashboard_server


def main():
    print("=" * 75)
    print("🚁 RESCUEPILOT — AUTONOMOUS AI MISSION COMMANDER (STRANDS AGENTS SDK)")
    print("   Good Neighbor Agents | Search & Rescue Multi-UAV Swarm Intelligence")
    print("=" * 75)

    try:
        server, port = run_dashboard_server(port=8080)
        url = f"http://localhost:{port}"
        print(f"✅ RescuePilot Tactical HUD active at: {url}")
        print("💡 Opening browser automatically...")
        print("Press Ctrl+C to stop the mission server.\n")

        # Open web browser after a short delay
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 RescuePilot Mission server stopped gracefully.")
    except Exception as e:
        print(f"\n❌ Error launching RescuePilot dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
