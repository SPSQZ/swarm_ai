"""One-command runner for the Drone Smart Path Mission Dashboard.

Usage:
    python run_dashboard.py
"""

import sys
import threading
import time
import webbrowser
from dashboard.server import run_dashboard_server


def main():
    print("=" * 70)
    print("🚁 DRONE SMART PATH — MISSION CONTROL DASHBOARD")
    print("=" * 70)

    try:
        server, port = run_dashboard_server(port=8080)
        url = f"http://localhost:{port}"
        print(f"✅ Dashboard Server active at: {url}")
        print("💡 Opening browser automatically...")
        print("Press Ctrl+C to stop the dashboard server.\n")

        # Open web browser after a short delay
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped gracefully.")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
