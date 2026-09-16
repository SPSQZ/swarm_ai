# 🚁 RescuePilot: Autonomous AI Mission Commander for Search-and-Rescue Drone Swarms

> **Bridging human emergency intent to autonomous multi-UAV swarm execution during disaster crises using the Strands Agents SDK.**

[![Hackathon: Agents for Humans](https://img.shields.io/badge/Hackathon-Agents%20for%20Humans-blueviolet.svg)](https://agentsforhumans.devpost.com/)
[![Track: Good Neighbor Agents](https://img.shields.io/badge/Track-Good%20Neighbor%20Agents-orange.svg)](#-inspiration-the-human-centric-crisis)
[![Framework: Strands Agents SDK](https://img.shields.io/badge/Agent%20SDK-Strands%20Agents-blue.svg)](https://github.com/strands-agents)
[![Tests: 86/86 Passing](https://img.shields.io/badge/Tests-86%2F86%20Passing-brightgreen.svg)](#-testing--verification)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Hardware: 100% Software-Based](https://img.shields.io/badge/Hardware-Simulation--First-orange.svg)](#-why-simulation-first)
[![Protocol: MAVLink v2 & QGC](https://img.shields.io/badge/Protocol-MAVLink%20v2%20%7C%20QGC%20.plan-purple.svg)](#-hardware-grounding-mavlink-v2--qgroundcontrol-export)
[![Dashboard: 2D/3D Live HUD](https://img.shields.io/badge/Dashboard-2D%2F3D%20Tactical%20HUD-cyan.svg)](#-interactive-2d3d-tactical-mission-hud)
[![Offline Ready: Zero-Key Fallback](https://img.shields.io/badge/Offline%20Ready-Zero--Key%20Engine-success.svg)](#-zero-key-resilience--cloud-engine)

---

## 📖 Table of Contents

- [💡 Inspiration: The Human-Centric Crisis](#-inspiration-the-human-centric-crisis)
- [⚙️ Closed-Loop Agentic Architecture](#️-closed-loop-agentic-architecture)
- [🛠️ The 7 Specialized Strands Agent Tools](#️-the-7-specialized-strands-agent-tools)
- [🛡️ "Honest Degradation" & Fault Tolerance](#️-honest-degradation--fault-tolerance)
- [🖥️ Interactive 2D/3D Tactical Mission HUD](#️-interactive-2d3d-tactical-mission-hud)
- [🔌 Zero-Key Resilience & Cloud Engine](#-zero-key-resilience--cloud-engine)
- [📡 Hardware Grounding: MAVLink v2 & QGroundControl Export](#-hardware-grounding-mavlink-v2--qgroundcontrol-export)
- [🚀 Quick Start (Run in 60 Seconds)](#-quick-start-run-in-60-seconds)
- [🧪 Testing & Verification](#-testing--verification)
- [🔬 The Underlying Robotics & Simulation Engine](#-the-underlying-robotics--simulation-engine)
- [📁 Repository Structure](#-repository-structure)
- [🎬 Demo Script & Evaluator Guide](#-demo-script--evaluator-guide)

---

## 💡 Inspiration: The Human-Centric Crisis

When a natural disaster strikes—such as a flash flood, wildfire, earthquake, or blizzard—every second matters. Search-and-Rescue (SAR) coordinators and emergency first responders face **extreme cognitive overload**:
- Calculating complex 3D flight trajectories and terrain clearance.
- Gauging dynamic wind-shear vectors and choosing aerodynamic formations.
- Tracking battery drain rates and communications dropouts.
- Triangulating thermal survivor signatures across rugged terrain.

### The Human Problem
Emergency personnel should **never** be forced to calculate waypoint coordinates, configure aerodynamic spacings, or fiddle with spreadsheet sliders while lives hang in the balance. They must operate at the level of **high-level human intent**.

### Enter RescuePilot
Powered by the **Strands Agents SDK**, **RescuePilot** acts as an expert Autonomous AI Mission Commander. It interprets natural language intent from human first responders, selects and chains specialized robotics tools, continuously monitors 3D environmental telemetry, dynamically replans when storms strike or drones fail (**"Honest Degradation"**), and exports production-grade flight plans for physical UAV hardware.

---

## ⚙️ Closed-Loop Agentic Architecture

Unlike traditional AI chatbots that generate static text responses, RescuePilot operates as a **continuous closed-loop agentic feedback system**:

```
                     ┌──────────────────────────────────────────────┐
                     │          Emergency Response Operator         │
                     │  "Deploy 4 drones to search northern sector. │
                     │   Prioritize survivor detection. Storm near."│
                     └──────────────────────┬───────────────────────┘
                                            │ Natural Language Intent
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │          RescuePilot Strands Agent           │
                     │        (Powered by Strands SDK)              │
                     │   • Multi-step Reasoning & Decomposition     │
                     │   • Model-Driven Tool Selection              │
                     │   • Dynamic Execution & Lifecycle Hooks      │
                     └──────────────────────┬───────────────────────┘
                                            │
        ┌───────────────────────────────────┴───────────────────────────────────┐
        ▼                                   ▼                                   ▼
┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
│WeatherAssessmentTool  │       │EnvironmentHazardTool  │       │ SwarmAllocationTool   │
│• Wind speed & gusts   │       │• 3D terrain elevation │       │• Fleet sizing & roles │
│• Storm progression    │       │• No-go zones & ridges │       │• Formation (Line/Arc) │
└───────────────────────┘       └───────────────────────┘       └───────────────────────┘
        ▼                                   ▼                                   ▼
┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
│   PathPlannerTool     │       │ SARInvestigationTool  │       │ FailureRecoveryTool   │
│• 3D motion primitives │       │• Frontier search grid │       │• GPS loss mitigation  │
│• Obstacle clearance   │       │• Survivor triage      │       │• Swarm re-balancing   │
└───────────────────────┘       └───────────────────────┘       └───────────────────────┘
                                            │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │              MissionReportTool               │
                     │  • SITREP generation & coverage telemetry    │
                     │  • MAVLink v2 & QGroundControl (.plan) export│
                     └──────────────────────┬───────────────────────┘
                                            │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │         3D Drone Swarm Simulation HUD        │
                     │  (Continuous Physics, Sensor Noise, Radar)   │
                     └──────────────────────┬───────────────────────┘
                                            │
                                            │ Real-Time Telemetry Triggers:
                                            │ ⚡ Sudden gale storm wind spike
                                            │ 🆘 Survivor detected at (55, 42)
                                            │ ⚠️ Drone Charlie GPS lost
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │      Continuous Observation & Re-planning    │
                     │  Strands Agent receives trigger -> Reasons   │
                     │  -> Invokes recovery tools -> Updates Swarm  │
                     └──────────────────────┴───────────────────────┘
```

---

## 🛠️ The 7 Specialized Strands Agent Tools

RescuePilot wraps its underlying robotics engine using the official `@tool` decorator from the Strands Agents SDK:

| # | Tool Name | Description | Key Capabilities |
|---|---|---|---|
| 1 | **`weather_assessment_tool`** | Analyzes atmospheric conditions and wind vectors | Computes safe flight speeds, identifies gust turbulence, and mandates aerodynamic Wedge formation under headwinds. |
| 2 | **`environment_hazard_tool`** | Evaluates 3D terrain Digital Elevation Models (DEM) | Detects ridge slope hazards, static obstacles, and restricted airspace (no-go zones) to enforce minimum terrain clearance. |
| 3 | **`swarm_allocation_tool`** | Dynamically configures multi-drone swarm geometry | Assigns Lead, Wing, and Tail roles and calculates formation spacing (Line for broad search, Wedge for storms, Arc/Diamond for tight corridors). |
| 4 | **`path_planning_tool`** | Synthesizes 3D kinematically feasible trajectories | Generates 3D motion primitives (climbs, turns, descents, straight dashes, hovers) with multi-objective safety costs. |
| 5 | **`sar_investigation_tool`** | Triangulates survivor signals and coordinates triage | Scores detection confidence, prioritizes life-critical targets, and plans automated 12-second high-resolution hover scans. |
| 6 | **`failure_recovery_tool`** | Orchestrates **Honest Degradation** | Safely isolates failing drones (optical-flow descent or RTB) and dynamically recalculates coverage spacing across survivors. |
| 7 | **`mission_report_tool`** | Compiles tactical military Situation Reports (SITREPs) | Synthesizes real-time mission telemetry and translates trajectories into QGroundControl `.plan` files and MAVLink v2 packets. |

---

## 🛡️ "Honest Degradation" & Fault Tolerance

Hackathon judges value real-world resilience over fragile "happy-path" demos. RescuePilot implements **Honest Degradation**:

- **Real-Time Anomaly Detection**: When a drone suffers sudden GPS signal degradation, motor stutter, or a critically depleted battery (<18%), the system does not crash or freeze.
- **Autonomous Safe Isolation**: The Strands Agent immediately invokes `failure_recovery_tool`, issuing an emergency command for the compromised UAV to switch to local optical flow and perform an immediate controlled descent or Return-to-Base (RTB).
- **Swarm Rebalancing**: The agent instantly reasons through the remaining active assets and rebalances the swarm (e.g., expanding 3-drone spacing from 5.0m to 6.2m) to ensure **zero coverage gaps** in the search grid.

---

## 🖥️ Interactive 2D/3D Tactical Mission HUD

RescuePilot includes an aerospace-grade, zero-dependency browser-based tactical command center (`HTML5 Canvas` + `Vanilla CSS`):

- **Dual Perspective Engine**: Seamless one-click toggling between **2D Top-Down Radar** and **3D Isometric Tactical View**.
- **Live Strands Reasoning Feed**: An integrated monospace HUD console displaying the agent's internal thoughts, tool invocations, parameters, and tactical rationale in real time.
- **Natural Language Intent Console**: Voice/text input bar with 4 one-click disaster presets for evaluators.
- **Dynamic Swarm Visualizer**: Animated quad-rotors, laser formation meshes, terrain elevation contours, obstacle 3D cylinders, and radar sweep sweeps.
- **Live Interactive Injector**: Real-time storm injector (gale wind spike) and fault matrix (GPS loss, comms blackout, low battery).
- **One-Click SITREP & Plan Export**: Instant modal displaying full military SITREPs and direct download of hardware-ready QGroundControl `.plan` files.

---

## 🔌 Zero-Key Resilience & Cloud Engine

A major pitfall of hackathon AI projects is failing during evaluation when judges lack specific cloud credentials. RescuePilot solves this with a **dual-engine architecture**:

1. **Amazon Bedrock (Cloud Engine)**:
   - Connects directly to Amazon Bedrock via `strands.models.bedrock.BedrockModel`.
   - Supports cutting-edge models like `amazon.nova-micro-v1:0` or Anthropic Claude 3.5 Haiku.
   - Automatically activates when AWS credentials (`AWS_ACCESS_KEY_ID` or `AWS_PROFILE`) are detected.
2. **Local Deterministic Engine (Zero-Key Fallback)**:
   - If no cloud credentials exist, RescuePilot seamlessly falls back to its built-in offline engine (`RescuePilotFallbackModel`).
   - Ensures **100% of features, tool calling, replanning, and dashboard interactions work immediately out of the box** without throwing errors or requiring API keys.

---

## 📡 Hardware Grounding: MAVLink v2 & QGroundControl Export

RescuePilot bridges software intelligence to physical aerospace hardware:
- **Official MAVLink v2 Binary Encoding**: Generates binary packets (`SET_POSITION_TARGET_LOCAL_NED` #84 and `HEARTBEAT` #0) ready for UDP streaming to PX4 SITL, ArduPilot, or physical telemetry radios.
- **QGroundControl `.plan` Exporter**: One-click download of standardized JSON mission files conforming to the QGroundControl v1 specification for immediate field upload.
- **Mission Planner WPL 110**: Generates legacy waypoint format files for older autopilot ground stations.

---

## 🚀 Quick Start (Run in 60 Seconds)

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/SPSQZ/swarm_ai.git
cd swarm_ai

# Install dependencies (strands-agents, numpy, matplotlib, pytest)
pip install -r requirements.txt
```

### 2. Launch the Mission Control Dashboard

```bash
python run_dashboard.py
```

This starts the tactical server at `http://localhost:8080` and automatically opens your web browser:
- Click **"🚨 1. Sector SAR Sweep"** to see the Strands Agent plan a 4-drone northern search mission.
- Click **"⚡ 2. Storm Evasion"** to watch the closed-loop agent reroute the swarm through a sheltered valley.
- Click **"⚠️ 4. Honest Degradation"** to inject a GPS failure on Drone Charlie and watch the agent isolate Charlie and rebalance the swarm!
- Click **"📜 SITREP"** to inspect and download the official QGroundControl flight plan.

*(Optional)* To run with Amazon Bedrock, simply export your AWS credentials before launching:
```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"
python run_dashboard.py
```

---

## 🧪 Testing & Verification

RescuePilot is verified with **86 comprehensive automated tests** across all subsystems:

```bash
pytest -v
```

### Test Suite Coverage:
| Test Suite | Tests | Description |
|---|:---:|---|
| `test_rescue_pilot_agent.py` | 10 | Strands Agent initialization, all 7 tools, fallback engine, and event logging |
| `test_mavlink_bridge.py` | 8 | MAVLink v2 packet framing, QGC `.plan` export, and coordinate conversions |
| `test_dashboard_server.py` | 4 | REST API endpoints, scenario resets, step advancement, and plan downloads |
| `test_intelligent_formation.py` | 4 | Dynamic formation switching, wind/terrain adaptation, and energy conservation |
| `test_phase1_to_17_*.py` | 60 | 3D physics, motion primitives, sensor noise, occupancy mapping, and SAR triage |
| **Total** | **86** | **100% Passing (~3.3s execution time)** |

---

## 🔬 The Underlying Robotics & Simulation Engine

Underneath the Strands Agent lies a high-fidelity simulation engine built from first principles:

1. **Continuous 3D Physics & Kinematics**:
   - 6-DOF state representation (position, velocity, acceleration, orientation angles, angular rates).
   - Non-linear battery discharge curves accounting for aerodynamic drag and payload weight.
2. **Perception & Mapping**:
   - 2D/3D probabilistic occupancy grids with log-odds sensor updates.
   - Digital Elevation Models (DEM) with slope roughness and traversability matrices.
   - Realistic sensor noise models (Gaussian drift on IMU, satellite degradation on GPS, LiDAR raycasting).
3. **Decentralized Swarm Coordination**:
   - Mesh telemetry broadcasting (state, battery, and target detections).
   - Pairwise collision evasion vectors preventing mid-air collisions.
   - Dynamic formation geometries (Line, Wedge, Arc, Diamond).

---

## 📁 Repository Structure

```
swarm_ai/
├── rescue_pilot/              # Strands Agents SDK Mission Commander
│   ├── agent.py               # Core RescuePilotAgent, BedrockModel hook, and fallback engine
│   ├── tools.py               # 7 specialized Strands @tool definitions
│   └── mission_events.py      # Telemetry event hooks and closed-loop triggers
│
├── dashboard/                 # Interactive 2D/3D Visual Mission HUD
│   ├── index.html             # Aerospace dark-mode command center layout
│   ├── style.css              # Cyber-aerospace HUD styling and glassmorphism
│   ├── app.js                 # 60 FPS HTML5 Canvas engine (2D Radar & 3D Isometric)
│   └── server.py              # REST API bridge and live simulation runner
│
├── interfaces/                # Autopilot & Hardware Protocol Bridges
│   └── mavlink_bridge.py      # MAVLink v2 binary frames & QGroundControl .plan export
│
├── swarm/                     # Swarm Coordination & Formation Geometry
│   ├── drone.py               # Swarm member entity
│   ├── swarm_coordinator.py   # Mesh telemetry & neighbor tracking
│   ├── formation.py           # Geometric formations (Line, Wedge, Arc, Diamond)
│   └── intelligent_formation.py # Dynamic context-aware formation advisor
│
├── planner/                   # 3D Path Planning & Trajectory Generation
│   ├── generator.py           # 3D motion primitives (turns, climbs, descents, hovers)
│   ├── validator.py           # Kinematic limits, boundary, and obstacle clearance
│   └── cost_function.py       # Multi-criteria path optimization
│
├── mapping/                   # Spatial Awareness & Traversability
│   ├── occupancy.py           # Probabilistic 2D/3D occupancy grid
│   ├── elevation.py           # Digital elevation model & gradient calculations
│   └── traversability.py      # Terrain cost assessment and corridor identification
│
├── rescue/                    # Search-and-Rescue Intelligence
│   ├── target_detector.py     # Thermal survivor detection and confidence scoring
│   └── investigation_planner.py # Priority hover-inspection planner
│
├── resilience/                # Fault Tolerance & Environmental Modeling
│   ├── weather_simulator.py   # Wind shear, gale gusts, and storm intensity
│   └── adaptive_controller.py # Dynamic speed throttling and formation contraction
│
├── simulation/                # World Physics & Entity Management
│   └── world.py               # Continuous 3D world physics and clock
│
├── tests/                     # 86 automated test suites (pytest)
│   ├── test_rescue_pilot_agent.py
│   ├── test_mavlink_bridge.py
│   └── test_phase*.py
│
├── run_dashboard.py           # 1-command launcher for visual mission HUD
├── requirements.txt           # Core Python dependencies
├── DEVPOST_SUBMISSION.md      # Official Devpost Hackathon submission copy
└── README.md                  # Master documentation
```

---

## 🎬 Demo Script & Evaluator Guide

For hackathon evaluators reviewing the submission, here is the recommended 3-minute walkthrough:

| Time | Action | What to Observe |
|---|---|---|
| **0:00 - 0:30** | Run `python run_dashboard.py` | Observe 3D isometric view, quad-rotor animations, and active UAV telemetry cards. |
| **0:30 - 1:15** | Click **"🚨 1. Sector SAR Sweep"** | Watch the Strands Agent reason through weather and terrain, select a Wedge formation, and stream its live thoughts on the HUD. |
| **1:15 - 2:00** | Click **"⚡ 2. Storm Evasion"** | Observe closed-loop adaptation: wind spikes trigger the agent to contract spacing to 4.5m and route through the valley corridor. |
| **2:00 - 2:40** | Click **"⚠️ 4. Honest Degradation"** | Witness fault tolerance: Drone Charlie loses GPS; the agent safely lands Charlie and rebalances the remaining 3 drones to eliminate gaps. |
| **2:40 - 3:00** | Click **"📜 SITREP"** | Review the tactical military situation report and download the official QGroundControl `.plan` file. |

---

## 📄 License

This project is licensed under the MIT License — open-source for search-and-rescue, first responders, and autonomous robotics researchers worldwide.
