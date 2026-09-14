# 🏆 Devpost Hackathon Submission: RescuePilot

**Hackathon**: [Agents for Humans](https://agentsforhumans.devpost.com/)  
**Track**: **Good Neighbor Agents** (Disaster Relief, First Responders, Search & Rescue)  
**Project Title**: **RescuePilot: Autonomous AI Mission Commander for Search-and-Rescue Drone Swarms**  
**Tagline**: Bridging human emergency intent to autonomous multi-UAV swarm execution during disaster crises using the Strands Agents SDK.

---

## 💡 Inspiration: The Human-Centric Crisis

When a natural disaster strikes—such as a flash flood, wildfire, earthquake, or blizzard—every second matters. Search-and-Rescue (SAR) coordinators and emergency first responders face **extreme cognitive overload**. 

While modern commercial drones exist, manually commanding a multi-UAV swarm in hostile weather is nearly impossible for an overwhelmed operator:
- Calculating 3D motion primitives and obstacle standoff distances
- Reading dynamic wind-shear vectors and choosing aerodynamic formations
- Balancing battery reserve thresholds and communications dropouts
- Correlating sensor feeds and triangulating survivor heat signatures

**The Human Problem**: Operators shouldn't be fiddling with coordinates, sliders, and waypoint spreadsheets while lives are on the line. They need to command at the level of **high-level human intent**, while an intelligent autonomous agent handles the spatial, physical, and multi-asset mathematics.

**Enter RescuePilot**: Powered by the **Strands Agents SDK**, RescuePilot serves as a tireless, expert AI Mission Commander that interprets plain English operator instructions, orchestrates a 7-tool domain suite, continuously observes the physical environment, dynamically replans when storms strike or drones fail ("Honest Degradation"), and exports hardware-ready flight plans for immediate field deployment.

---

## ⚙️ How It Works: The Closed-Loop Agentic Architecture

Unlike traditional AI wrappers that simply reply with static text, RescuePilot implements a **continuous closed-loop agentic cycle**:

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
                     │   • Dynamic Execution & Event Hooks          │
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
                                            │ Telemetry Triggers & Events:
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

RescuePilot wraps its robotics simulation using the official `@tool` decorator from the Strands SDK:

1. **`weather_assessment_tool`**: Evaluates ambient wind vectors, gust turbulence, and visibility. Calculates safe flight speeds and recommends formation constraints (e.g. aerodynamic Wedge formation for headwind stability).
2. **`environment_hazard_tool`**: Scans 3D Digital Elevation Models (DEM), ridge slope hazards, static obstacles, and restricted airspace (no-go zones) to establish guaranteed safe corridors.
3. **`swarm_allocation_tool`**: Allocates drone roles (Lead, Wing, Tail), calculates dynamic inter-drone spacing, and determines formation geometry:
   - **Line Formation**: Maximizes sensor search coverage under calm conditions.
   - **Wedge Formation**: Penetrates headwinds and storms with contracted spacing.
   - **Arc / Diamond Formation**: Tight perimeter sweeps and close-quarters obstacle navigation.
4. **`path_planning_tool`**: Generates 3D kinematically feasible waypoints with boundary constraints, obstacle clearance, and minimum terrain altitude margins.
5. **`sar_investigation_tool`**: Maintains target detection confidence ratings, prioritizes survivor signals, and synthesizes 12-second high-resolution hover-scan flight plans.
6. **`failure_recovery_tool` ("Honest Degradation")**: When a drone experiences GPS degradation, battery depletion (<18%), or motor anomalies:
   - Orders safe isolation (optical flow landing or direct-azimuth Return-to-Base).
   - Autonomously degrades and rebalances the remaining swarm (e.g. expanding 3-drone spacing by +20% to prevent search grid gaps).
7. **`mission_report_tool`**: Compiles real-time tactical military Situation Reports (SITREPs) and translates active swarm paths into industry-standard **QGroundControl JSON mission plans (`.plan`)** and **MAVLink v2 binary frames** for real hardware.

---

## 🛡️ "Honest Degradation" & Fault Tolerance

The hackathon judging guidelines explicitly value resilience over brittle "happy path" demos. RescuePilot demonstrates **Honest Degradation**:
- If Drone Bravo loses GPS lock mid-mission, the human operator doesn't need to manually intervene.
- The Strands Agent detects the anomaly, reasons through contingency options, commands Drone Bravo to execute an optical-flow controlled descent, and instantly reconfigures Alpha, Charlie, and Delta into a balanced 3-drone formation with expanded coverage spacing.

---

## 🖥️ Live Tactical Mission Dashboard

The system includes a zero-dependency, browser-based tactical HUD:
- **Dual Perspective**: Real-time toggling between **2D Top-Down Radar** and **3D Isometric View**.
- **Live Strands Reasoning Trace**: Monospace HUD terminal displaying the agent's internal thoughts, tool invocations, parameters, and tactical rationale in real time.
- **Natural Language Intent Input**: Voice/text command bar with 1-click disaster presets.
- **Military SITREP Modal**: Instant generation and download of QGroundControl `.plan` files.

---

## 🚀 How We Built It

- **Strands Agents SDK (`strands-agents`)**: Core model-driven orchestration, `@tool` schema generation, dynamic tool calling, and lifecycle hooks.
- **Model Engine**: Primary support for **Amazon Bedrock** (`amazon.nova-micro-v1:0` or `anthropic.claude-3-haiku`) with a built-in deterministic offline fallback engine (`RescuePilotFallbackModel`) for zero-key evaluation.
- **Simulation Engine**: Continuous 3D physics, terrain elevation gradients, sensor noise simulation (IMU, GPS, LiDAR, RGB camera), and decentralized collision evasion.
- **Hardware Protocols**: MAVLink v2 binary packet encoding (`SET_POSITION_TARGET_LOCAL_NED`) and QGroundControl `.plan` JSON exporter.
- **Frontend HUD**: Vanilla HTML5 Canvas & Cyber-HUD CSS (zero heavyweight frontend frameworks).

---

## 🧪 Verification & Testing

- **Automated Tests**: 86 passing tests (`pytest -v`), including dedicated tests for all 7 Strands tools, agent command parsing, closed-loop replanning, and MAVLink generation.
- **100% Software-Based**: Can be completely run, inspected, and verified on any standard machine without physical drone hardware.

---

## 🎬 3-Minute Video Demo Script (For Devpost Submission)

| Time | Scene | Narration / Script |
| :--- | :--- | :--- |
| **0:00 - 0:35** | **The Crisis & Problem**<br>*(Show title slide & disaster context)* | *"When a flash flood or hurricane hits, first responders face impossible odds. Searching rugged terrain with drone swarms requires calculating wind drift, avoiding ridges, and tracking battery levels—all while lives hang in the balance. Manual piloting cannot scale to multi-UAV crisis response. That's why we built **RescuePilot**."* |
| **0:35 - 1:15** | **Natural Language Intent to Multi-Tool Execution**<br>*(Show dashboard, click Preset 1 or type prompt)* | *"Watch what happens when the emergency operator inputs high-level intent: 'Deploy four drones to search the northern sector. Prioritize survivor detection. A storm is approaching.'<br>RescuePilot, powered by the **Strands Agents SDK**, breaks down this intent. It reasons through atmospheric risks with the `weather_assessment_tool`, verifies terrain in `environment_hazard_tool`, allocates a 4-drone Wedge formation in `swarm_allocation_tool`, and plans 3D waypoints in `path_planning_tool`. Look at the live Strands reasoning trace streaming on the HUD."* |
| **1:15 - 2:05** | **Dynamic Environmental Feedback & Replanning**<br>*(Click 'Inject Gale Storm' or show survivor detection)* | *"Notice how RescuePilot doesn't stop after planning. This is a true closed-loop agent. When our simulation detects a sudden wind spike exceeding 14 m/s, an environmental trigger feeds into the Strands Agent. The agent immediately reasons: wind is critical, contracts the formation spacing to 4.5 meters, and routes the drones through the sheltered valley corridor."* |
| **2:05 - 2:35** | **Honest Degradation (Fault Tolerance)**<br>*(Click 'GPS Loss' on Drone Charlie)* | *"Now for what sets RescuePilot apart: **Honest Degradation**. We inject a sudden GPS failure on Drone Charlie. Instead of crashing or halting, RescuePilot invokes `failure_recovery_tool`, orders Charlie to safely land using optical flow, and autonomously rebalances the remaining 3 drones into an expanded search grid to ensure zero coverage gaps."* |
| **2:35 - 3:00** | **Hardware Readiness & Wrap-up**<br>*(Open SITREP modal, show QGC .plan download)* | *"Finally, RescuePilot generates a complete military SITREP and exports the mission directly as a standard QGroundControl `.plan` and MAVLink v2 binary stream, ready for immediate upload to physical PX4 or ArduPilot drones.<br>RescuePilot: Putting the power of autonomous AI swarms into the hands of the heroes saving human lives."* |
