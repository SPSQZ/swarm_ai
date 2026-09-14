/**
 * Drone Smart Path — Mission Control Canvas & HUD Engine
 * High-performance 2D/3D visual flight visualizer & telemetry synchronizer.
 */

(function () {
  'use strict';

  // State
  let simState = null;
  let is3DView = true;
  let isPlaying = true;
  let zoomLevel = 1.0;
  let panOffset = { x: 0, y: 0 };
  let isDragging = false;
  let dragStart = { x: 0, y: 0 };
  let rotorAngle = 0.0;
  let lastServerSync = Date.now();
  let offlineTime = 0.0;

  // Weather Particles
  const weatherParticles = [];
  const NUM_PARTICLES = 120;

  // DOM Elements
  const canvas = document.getElementById('mission-canvas');
  const ctx = canvas.getContext('2d');

  // HUD Elements
  const txtMissionStatus = document.getElementById('txt-mission-status');
  const txtFormationType = document.getElementById('txt-formation-type');
  const txtWeatherSummary = document.getElementById('txt-weather-summary');
  const txtMissionTime = document.getElementById('txt-mission-time');
  const valCoverage = document.getElementById('val-coverage');
  const barCoverage = document.getElementById('bar-coverage');
  const valDistance = document.getElementById('val-distance');
  const valSpacing = document.getElementById('val-spacing');
  const droneCardList = document.getElementById('drone-card-list');
  const targetList = document.getElementById('target-list');
  const compassNeedle = document.getElementById('compass-needle');
  const txtWindSpeed = document.getElementById('txt-wind-speed');
  const rngWind = document.getElementById('rng-wind');
  const badgeStorm = document.getElementById('badge-storm-status');
  const btnTogglePlay = document.getElementById('btn-toggle-play');
  const iconPlayPause = document.getElementById('icon-play-pause');
  const lblPlayPause = document.getElementById('lbl-play-pause');
  const btnViewToggle = document.getElementById('btn-view-toggle');
  const lblViewMode = document.getElementById('lbl-view-mode');
  const selScenario = document.getElementById('sel-scenario');
  const chkAutoFormation = document.getElementById('chk-auto-formation');

  // RescuePilot Agent Console Elements
  const txtAgentStatus = document.getElementById('txt-agent-status');
  const inputAgentPrompt = document.getElementById('input-agent-prompt');
  const btnAgentDispatch = document.getElementById('btn-agent-dispatch');
  const agentTraceFeed = document.getElementById('agent-trace-feed');
  const traceEventCount = document.getElementById('trace-event-count');
  const agentTraceContainer = document.getElementById('agent-trace-container');
  const btnToggleTrace = document.getElementById('btn-toggle-trace');
  const lblToggleTrace = document.getElementById('lbl-toggle-trace');
  const modalSitrep = document.getElementById('modal-sitrep');
  const sitrepContent = document.getElementById('sitrep-content');
  const btnOpenSitrep = document.getElementById('btn-open-sitrep');
  const btnCloseSitrep = document.getElementById('btn-close-sitrep');
  const btnCopySitrep = document.getElementById('btn-copy-sitrep');
  let lastTraceCount = 0;

  // Initialize Particles
  for (let i = 0; i < NUM_PARTICLES; i++) {
    weatherParticles.push({
      x: Math.random() * 2000 - 500,
      y: Math.random() * 2000 - 500,
      length: Math.random() * 18 + 6,
      speed: Math.random() * 2 + 1,
    });
  }

  // Handle Canvas Resizing
  function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  // ---------------------------------------------------------------------------
  // Coordinate Projections: 2D Flat vs 3D Isometric
  // ---------------------------------------------------------------------------
  function worldToScreen(wx, wy, wz = 0) {
    const cx = canvas.width / 2 + panOffset.x;
    const cy = canvas.height / 2 + panOffset.y;
    const scale = (Math.min(canvas.width, canvas.height) / 140) * zoomLevel;

    // Center world (120x120) at (60, 60)
    const normX = wx - 60;
    const normY = wy - 60;

    if (!is3DView) {
      // 2D Top-Down View
      return {
        x: cx + normX * scale,
        y: cy + normY * scale,
        scale: scale,
      };
    } else {
      // 3D Isometric Perspective View
      const isoAngle = Math.PI / 6; // 30 degrees
      const cosA = Math.cos(isoAngle);
      const sinA = Math.sin(isoAngle);

      const isoX = (normX - normY) * cosA;
      const isoY = (normX + normY) * sinA - wz * 0.9;

      return {
        x: cx + isoX * scale * 1.15,
        y: cy + isoY * scale * 1.15 + 20,
        scale: scale,
      };
    }
  }

  // ---------------------------------------------------------------------------
  // Canvas Rendering Loops
  // ---------------------------------------------------------------------------
  function drawGrid() {
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;

    const gridSize = 10;
    const maxCoord = 120;

    for (let x = 0; x <= maxCoord; x += gridSize) {
      const p1 = worldToScreen(x, 0, 0);
      const p2 = worldToScreen(x, maxCoord, 0);
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    }

    for (let y = 0; y <= maxCoord; y += gridSize) {
      const p1 = worldToScreen(0, y, 0);
      const p2 = worldToScreen(maxCoord, y, 0);
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    }

    // World Boundary
    const b0 = worldToScreen(0, 0, 0);
    const b1 = worldToScreen(maxCoord, 0, 0);
    const b2 = worldToScreen(maxCoord, maxCoord, 0);
    const b3 = worldToScreen(0, maxCoord, 0);

    ctx.strokeStyle = 'rgba(0, 242, 254, 0.35)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(b0.x, b0.y);
    ctx.lineTo(b1.x, b1.y);
    ctx.lineTo(b2.x, b2.y);
    ctx.lineTo(b3.x, b3.y);
    ctx.closePath();
    ctx.stroke();

    ctx.restore();
  }

  function drawNoGoZones(zones) {
    if (!zones) return;
    ctx.save();
    zones.forEach(z => {
      const p1 = worldToScreen(z.x1, z.y1, 0);
      const p2 = worldToScreen(z.x2, z.y1, 0);
      const p3 = worldToScreen(z.x2, z.y2, 0);
      const p4 = worldToScreen(z.x1, z.y2, 0);

      ctx.fillStyle = 'rgba(239, 68, 68, 0.12)';
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)';
      ctx.lineWidth = 1.5;

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.lineTo(p3.x, p3.y);
      ctx.lineTo(p4.x, p4.y);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Label
      const mid = worldToScreen((z.x1 + z.x2) / 2, (z.y1 + z.y2) / 2, 0);
      ctx.fillStyle = '#ef4444';
      ctx.font = '600 10px Outfit';
      ctx.textAlign = 'center';
      ctx.fillText(z.label || 'NO-GO ZONE', mid.x, mid.y);
    });
    ctx.restore();
  }

  function drawObstacles(obstacles) {
    if (!obstacles) return;
    ctx.save();
    obstacles.forEach(obs => {
      const base = worldToScreen(obs.x, obs.y, 0);
      const top = worldToScreen(obs.x, obs.y, obs.height || 20);
      const r = (obs.radius || 6) * base.scale;

      // Base shadow / bottom circle
      ctx.fillStyle = 'rgba(15, 23, 42, 0.7)';
      ctx.beginPath();
      ctx.arc(base.x, base.y, r, 0, Math.PI * 2);
      ctx.fill();

      if (is3DView) {
        // Extruded 3D cylinder
        ctx.fillStyle = 'rgba(71, 85, 105, 0.35)';
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)';
        ctx.lineWidth = 1.2;

        ctx.beginPath();
        ctx.moveTo(base.x - r, base.y);
        ctx.lineTo(top.x - r, top.y);
        ctx.lineTo(top.x + r, top.y);
        ctx.lineTo(base.x + r, base.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Cylinder Cap
        ctx.fillStyle = 'rgba(100, 116, 139, 0.65)';
        ctx.beginPath();
        ctx.arc(top.x, top.y, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      } else {
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.7)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(base.x, base.y, r, 0, Math.PI * 2);
        ctx.stroke();
      }
    });
    ctx.restore();
  }

  function drawTargets(targets) {
    if (!targets) return;
    ctx.save();
    const timeSec = Date.now() / 1000;

    targets.forEach(t => {
      const pos = worldToScreen(t.x, t.y, t.z || 0);

      // Expanding radar beacon wave
      const wavePhase = (timeSec * 1.5 + t.id) % 2;
      const waveRadius = wavePhase * 24 + 4;
      const waveAlpha = Math.max(0, 1 - wavePhase / 2);

      ctx.strokeStyle = `rgba(245, 158, 11, ${waveAlpha})`;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, waveRadius, 0, Math.PI * 2);
      ctx.stroke();

      // Center Pin Marker
      ctx.fillStyle = '#f59e0b';
      ctx.shadowColor = '#f59e0b';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 5, 0, Math.PI * 2);
      ctx.fill();

      // Target Label
      ctx.shadowBlur = 0;
      ctx.fillStyle = '#ffffff';
      ctx.font = '700 10px Outfit';
      ctx.textAlign = 'center';
      ctx.fillText(`${t.type} (${Math.round(t.confidence * 100)}%)`, pos.x, pos.y - 12);
    });
    ctx.restore();
  }

  function drawFormationLinks(drones) {
    if (!drones || drones.length < 2) return;
    ctx.save();
    ctx.strokeStyle = 'rgba(0, 242, 254, 0.3)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);

    const leadScreen = worldToScreen(drones[0].x, drones[0].y, drones[0].z);

    for (let i = 1; i < drones.length; i++) {
      const followerScreen = worldToScreen(drones[i].x, drones[i].y, drones[i].z);
      ctx.beginPath();
      ctx.moveTo(leadScreen.x, leadScreen.y);
      ctx.lineTo(followerScreen.x, followerScreen.y);
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawDrones(drones) {
    if (!drones) return;
    ctx.save();

    drones.forEach((drone, idx) => {
      const isLead = idx === 0;
      const pos = worldToScreen(drone.x, drone.y, drone.z);
      const groundPos = worldToScreen(drone.x, drone.y, 0);

      // Altitude Tether / Drop-line in 3D
      if (is3DView && drone.z > 0) {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.setLineDash([2, 3]);
        ctx.beginPath();
        ctx.moveTo(groundPos.x, groundPos.y);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
        ctx.setLineDash([]);

        // Ground shadow dot
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.beginPath();
        ctx.arc(groundPos.x, groundPos.y, 4, 0, Math.PI * 2);
        ctx.fill();
      }

      // Drone Heading Angle
      const heading = Math.atan2(drone.vy || 0, drone.vx || 0);

      // Drone Body Cross Frame
      const size = isLead ? 11 : 9;
      const color = drone.status === 'nominal' ? (isLead ? '#00f2fe' : '#38bdf8') : '#ef4444';

      ctx.save();
      ctx.translate(pos.x, pos.y);
      ctx.rotate(heading);

      // Safety Halo Bubble
      ctx.fillStyle = isLead ? 'rgba(0, 242, 254, 0.08)' : 'rgba(56, 189, 248, 0.06)';
      ctx.beginPath();
      ctx.arc(0, 0, size * 2.2, 0, Math.PI * 2);
      ctx.fill();

      // Arms (X-Frame)
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(-size, -size);
      ctx.lineTo(size, size);
      ctx.moveTo(size, -size);
      ctx.lineTo(-size, size);
      ctx.stroke();

      // Spinning Rotors
      const rotorRadius = size * 0.45;
      const armOffsets = [
        { x: -size, y: -size },
        { x: size, y: -size },
        { x: size, y: size },
        { x: -size, y: size },
      ];

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.lineWidth = 1.2;

      armOffsets.forEach(arm => {
        ctx.beginPath();
        ctx.arc(arm.x, arm.y, rotorRadius, 0, Math.PI * 2);
        ctx.stroke();

        // Spinning blade lines
        ctx.beginPath();
        const bX = Math.cos(rotorAngle) * rotorRadius;
        const bY = Math.sin(rotorAngle) * rotorRadius;
        ctx.moveTo(arm.x - bX, arm.y - bY);
        ctx.lineTo(arm.x + bX, arm.y + bY);
        ctx.stroke();
      });

      // Central Hub
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = color;
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.arc(0, 0, 3.5, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();

      // Telemetry Callout Tag
      ctx.fillStyle = '#ffffff';
      ctx.font = '600 10px JetBrains Mono';
      ctx.textAlign = 'center';
      ctx.shadowBlur = 0;
      ctx.fillText(`${drone.name || 'UAV'} (${Math.round(drone.z)}m)`, pos.x, pos.y - 14);
    });

    ctx.restore();
  }

  function drawWeatherParticles(weather) {
    if (!weather) return;
    const windSpeed = weather.wind_speed || 3.0;
    const windAngle = ((weather.wind_dir || 45) * Math.PI) / 180;
    const cosW = Math.cos(windAngle);
    const sinW = Math.sin(windAngle);

    ctx.save();
    ctx.strokeStyle = weather.storm ? 'rgba(200, 225, 255, 0.45)' : 'rgba(0, 242, 254, 0.2)';
    ctx.lineWidth = weather.storm ? 1.5 : 1.0;

    weatherParticles.forEach(p => {
      p.x += cosW * windSpeed * p.speed * 0.7;
      p.y += sinW * windSpeed * p.speed * 0.7;

      if (p.x > canvas.width + 100) p.x = -100;
      if (p.x < -100) p.x = canvas.width + 100;
      if (p.y > canvas.height + 100) p.y = -100;
      if (p.y < -100) p.y = canvas.height + 100;

      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      ctx.lineTo(p.x + cosW * p.length, p.y + sinW * p.length);
      ctx.stroke();
    });

    ctx.restore();
  }

  // ---------------------------------------------------------------------------
  // Master Animation Loop
  // ---------------------------------------------------------------------------
  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    rotorAngle += 0.45;

    // Draw Simulation Layers
    drawGrid();

    if (simState) {
      drawNoGoZones(simState.no_go_zones);
      drawObstacles(simState.obstacles);
      drawTargets(simState.targets);
      drawFormationLinks(simState.drones);
      drawDrones(simState.drones);
      drawWeatherParticles(simState.weather);
    }

    requestAnimationFrame(render);
  }
  requestAnimationFrame(render);

  // ---------------------------------------------------------------------------
  // HUD UI Updates
  // ---------------------------------------------------------------------------
  function updateHUD(state) {
    if (!state) return;

    // Time Formatting
    const totalSec = Math.floor(state.time || 0);
    const mins = String(Math.floor(totalSec / 60)).padStart(2, '0');
    const secs = String(totalSec % 60).padStart(2, '0');
    const frac = String(Math.floor(((state.time || 0) % 1) * 10));
    txtMissionTime.innerText = `${mins}:${secs}.${frac}`;

    // Metrics
    if (state.metrics) {
      valCoverage.innerText = state.metrics.coverage_pct.toFixed(1);
      barCoverage.style.width = `${state.metrics.coverage_pct}%`;
      valDistance.innerText = state.metrics.total_distance.toFixed(1);
    }

    // Formation
    if (state.formation) {
      txtFormationType.innerText = `${state.formation.type.toUpperCase()} ${state.formation.auto ? '(AUTO)' : ''}`;
      valSpacing.innerText = state.formation.spacing.toFixed(1);

      // Update button active state
      document.querySelectorAll('.btn-formation').forEach(b => {
        b.classList.toggle('active', b.dataset.formation === state.formation.type);
      });
    }

    // Weather
    if (state.weather) {
      txtWeatherSummary.innerText = `WIND ${state.weather.wind_speed} m/s`;
      txtWindSpeed.innerText = `${state.weather.wind_speed} m/s`;
      rngWind.value = state.weather.wind_speed;
      badgeStorm.innerText = state.weather.storm ? 'GALE STORM' : 'NORMAL';
      badgeStorm.classList.toggle('badge-accent', state.weather.storm);

      // Rotate Compass Needle
      compassNeedle.style.transform = `rotate(${state.weather.wind_dir || 0}deg)`;
    }

    // Drone Telemetry Cards
    if (state.drones) {
      droneCardList.innerHTML = '';
      state.drones.forEach((d, idx) => {
        const card = document.createElement('div');
        const isLead = idx === 0;
        const isFailed = d.status !== 'nominal';

        card.className = `drone-card ${isLead ? 'lead' : 'wing'} ${isFailed ? 'failed' : ''}`;

        const battColor = d.battery > 50 ? '#10b981' : d.battery > 25 ? '#f59e0b' : '#ef4444';

        card.innerHTML = `
          <div class="drone-card-header">
            <div class="drone-name-row">
              <span class="drone-id-tag">#${d.id}</span>
              <span class="drone-title">${d.name}</span>
            </div>
            <span class="drone-status-tag ${isFailed ? 'warn' : ''}">${d.status.toUpperCase()}</span>
          </div>
          <div class="drone-telemetry-row">
            <span>POS: [${d.x.toFixed(1)}, ${d.y.toFixed(1)}]</span>
            <span>ALT: ${d.z.toFixed(1)}m</span>
            <span>SPD: ${Math.hypot(d.vx || 0, d.vy || 0).toFixed(1)} m/s</span>
          </div>
          <div class="battery-row">
            <div class="battery-bar-outer">
              <div class="battery-bar-inner" style="width: ${d.battery}%; background: ${battColor};"></div>
            </div>
            <span style="font-size: 0.7rem; font-family: var(--font-mono); font-weight: 700;">${Math.round(d.battery)}%</span>
          </div>
        `;
        droneCardList.appendChild(card);
      });
    }

    // SAR Targets
    if (state.targets) {
      targetList.innerHTML = '';
      state.targets.forEach(t => {
        const item = document.createElement('div');
        item.className = 'target-item';
        item.innerHTML = `
          <span style="font-weight: 600;">${t.type}</span>
          <span class="target-badge ${t.status === 'unconfirmed' ? 'unconfirmed' : ''}">${t.status.toUpperCase()}</span>
        `;
        targetList.appendChild(item);
      });
    }

    // RescuePilot Strands Agent Trace & Status
    if (state.agent) {
      if (txtAgentStatus && state.agent.mission_state) {
        txtAgentStatus.innerText = `COMMANDER: ${state.agent.mission_state.status || 'ACTIVE'}`;
      }
      renderAgentTrace(state.agent.recent_trace);
    }
  }

  function renderAgentTrace(trace) {
    if (!trace || !Array.isArray(trace) || !agentTraceFeed) return;
    if (trace.length === lastTraceCount) return;
    lastTraceCount = trace.length;

    if (traceEventCount) traceEventCount.innerText = `${trace.length} EVENTS`;
    agentTraceFeed.innerHTML = '';

    trace.forEach(entry => {
      const row = document.createElement('div');
      row.className = 'trace-entry';

      let pillClass = 'pill-tool-call';
      if (entry.type === 'OPERATOR_INPUT') pillClass = 'pill-dispatch';
      else if (entry.type === 'REASONING') pillClass = 'pill-reasoning';
      else if (entry.type === 'TOOL_CALL') pillClass = 'pill-tool-call';
      else if (entry.type === 'TOOL_RESULT') pillClass = 'pill-tool-result';
      else if (entry.type === 'REPLAN_TRIGGER') pillClass = 'pill-replan';
      else if (entry.type === 'MISSION_DISPATCH' || entry.type === 'ACTION_TAKEN') pillClass = 'pill-dispatch';

      let detailsStr = '';
      if (typeof entry.details === 'object' && entry.details !== null) {
        try {
          detailsStr = JSON.stringify(entry.details);
        } catch (e) {
          detailsStr = String(entry.details);
        }
      } else if (entry.details) {
        detailsStr = String(entry.details);
      }

      row.innerHTML = `
        <span class="trace-time font-mono">${entry.timestamp || ''}</span>
        <span class="trace-pill ${pillClass}">${entry.type}</span>
        <div class="trace-body">
          <span class="trace-title">${entry.title}:</span>
          <span class="trace-details">${detailsStr}</span>
        </div>
      `;
      agentTraceFeed.appendChild(row);
    });

    agentTraceFeed.scrollTop = agentTraceFeed.scrollHeight;
  }

  // ---------------------------------------------------------------------------
  // REST API Syncing with Server
  // ---------------------------------------------------------------------------
  async function syncServer() {
    try {
      const resp = await fetch('/api/state');
      if (resp.ok) {
        simState = await resp.json();
        updateHUD(simState);
        lastServerSync = Date.now();
      }
    } catch (err) {
      // Offline fallback: simulate smooth movement locally if standalone
      runOfflineFallback();
    }
  }
  setInterval(syncServer, 100);

  function runOfflineFallback() {
    offlineTime += 0.1;
    if (!simState) {
      simState = {
        running: true,
        time: offlineTime,
        drones: [
          { id: 1, name: 'Alpha (Lead)', x: 60 + Math.cos(offlineTime * 0.5) * 30, y: 60 + Math.sin(offlineTime * 0.5) * 30, z: 14, vx: 2, vy: 2, battery: 95, status: 'nominal' },
          { id: 2, name: 'Bravo', x: 55 + Math.cos(offlineTime * 0.5) * 30, y: 55 + Math.sin(offlineTime * 0.5) * 30, z: 14, vx: 2, vy: 2, battery: 94, status: 'nominal' },
          { id: 3, name: 'Charlie', x: 55 + Math.cos(offlineTime * 0.5) * 30, y: 65 + Math.sin(offlineTime * 0.5) * 30, z: 14, vx: 2, vy: 2, battery: 92, status: 'nominal' },
          { id: 4, name: 'Delta', x: 50 + Math.cos(offlineTime * 0.5) * 30, y: 60 + Math.sin(offlineTime * 0.5) * 30, z: 14, vx: 2, vy: 2, battery: 91, status: 'nominal' },
        ],
        formation: { type: 'wedge', spacing: 6.0, auto: true },
        weather: { wind_speed: 4.5, wind_dir: 45, storm: false },
        obstacles: [
          { x: 35, y: 30, radius: 6, height: 25 },
          { x: 65, y: 60, radius: 8, height: 30 },
          { x: 85, y: 35, radius: 5, height: 18 },
        ],
        no_go_zones: [{ x1: 50, y1: 10, x2: 65, y2: 25, label: 'RESTRICTED AIRSPACE' }],
        targets: [
          { id: 1, type: 'Survivor', x: 55, y: 42, confidence: 0.94, status: 'investigated' },
          { id: 2, type: 'Beacon', x: 88, y: 78, confidence: 0.82, status: 'detected' },
        ],
        metrics: { total_distance: offlineTime * 4.2, coverage_pct: Math.min(100, offlineTime * 1.5) },
      };
    } else {
      simState.time = offlineTime;
      simState.drones[0].x = 60 + Math.cos(offlineTime * 0.5) * 30;
      simState.drones[0].y = 60 + Math.sin(offlineTime * 0.5) * 30;
      simState.drones[1].x = simState.drones[0].x - 5;
      simState.drones[1].y = simState.drones[0].y - 5;
      simState.drones[2].x = simState.drones[0].x - 5;
      simState.drones[2].y = simState.drones[0].y + 5;
      simState.drones[3].x = simState.drones[0].x - 10;
      simState.drones[3].y = simState.drones[0].y;
    }
    updateHUD(simState);
  }

  async function sendCommand(cmd) {
    try {
      await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cmd),
      });
      syncServer();
    } catch (err) {
      console.warn('Command dispatched offline:', cmd);
    }
  }

  // ---------------------------------------------------------------------------
  // User Event Listeners
  // ---------------------------------------------------------------------------
  btnTogglePlay.addEventListener('click', () => {
    isPlaying = !isPlaying;
    iconPlayPause.innerText = isPlaying ? '⏸' : '▶';
    lblPlayPause.innerText = isPlaying ? 'PAUSE' : 'RESUME';
    sendCommand({ action: isPlaying ? 'play' : 'pause' });
  });

  document.getElementById('btn-step').addEventListener('click', () => {
    sendCommand({ action: 'step' });
  });

  document.getElementById('btn-reset').addEventListener('click', () => {
    sendCommand({ action: 'reset' });
  });

  btnViewToggle.addEventListener('click', () => {
    is3DView = !is3DView;
    lblViewMode.innerText = is3DView ? '3D VIEW' : '2D VIEW';
  });

  // Formation Buttons
  document.querySelectorAll('.btn-formation').forEach(btn => {
    btn.addEventListener('click', () => {
      const fType = btn.dataset.formation;
      sendCommand({ action: 'set_formation', formation: fType, auto: false });
      chkAutoFormation.checked = false;
    });
  });

  chkAutoFormation.addEventListener('change', e => {
    sendCommand({ action: 'set_formation', formation: 'wedge', auto: e.target.checked });
  });

  // Weather Range Slider
  rngWind.addEventListener('input', e => {
    const spd = parseFloat(e.target.value);
    txtWindSpeed.innerText = `${spd} m/s`;
    sendCommand({ action: 'inject_weather', wind_speed: spd, storm: spd > 9.0 });
  });

  // Weather Injection (Linked to Closed-Loop Agent Observation)
  document.getElementById('btn-inject-storm').addEventListener('click', async () => {
    rngWind.value = 16.0;
    txtWindSpeed.innerText = '16.0 m/s';
    try {
      await fetch('/api/agent/trigger_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_type: 'WEATHER_ALERT', data: { wind_speed: 16.0 } }),
      });
      syncServer();
    } catch (e) {
      sendCommand({ action: 'inject_weather', wind_speed: 16.0, storm: true });
    }
  });

  document.getElementById('btn-clear-weather').addEventListener('click', () => {
    rngWind.value = 2.0;
    txtWindSpeed.innerText = '2.0 m/s';
    sendCommand({ action: 'inject_weather', wind_speed: 2.0, storm: false });
  });

  // Failure Injection Buttons (Linked to Agent Honest Degradation)
  document.getElementById('btn-fail-gps').addEventListener('click', async () => {
    try {
      await fetch('/api/agent/trigger_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_type: 'DRONE_FAILURE', data: { drone_id: 2, failure_type: 'gps_loss' } }),
      });
      syncServer();
    } catch (e) {
      sendCommand({ action: 'inject_failure', type: 'gps_loss', drone_id: 2 });
    }
  });

  document.getElementById('btn-fail-comms').addEventListener('click', async () => {
    try {
      await fetch('/api/agent/trigger_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_type: 'DRONE_FAILURE', data: { drone_id: 3, failure_type: 'comms_loss' } }),
      });
      syncServer();
    } catch (e) {
      sendCommand({ action: 'inject_failure', type: 'comms_loss', drone_id: 3 });
    }
  });

  document.getElementById('btn-fail-battery').addEventListener('click', async () => {
    try {
      await fetch('/api/agent/trigger_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_type: 'DRONE_FAILURE', data: { drone_id: 4, failure_type: 'battery_critical' } }),
      });
      syncServer();
    } catch (e) {
      sendCommand({ action: 'inject_failure', type: 'low_battery', drone_id: 4 });
    }
  });

  // RescuePilot Natural Language Dispatch
  async function dispatchAgentPrompt(prompt) {
    if (!prompt || !prompt.trim()) return;
    const cleanPrompt = prompt.trim();
    if (inputAgentPrompt) inputAgentPrompt.value = cleanPrompt;
    if (btnAgentDispatch) btnAgentDispatch.disabled = true;
    if (txtAgentStatus) txtAgentStatus.innerText = 'COMMANDER: REASONING...';

    try {
      const resp = await fetch('/api/agent/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: cleanPrompt }),
      });
      if (resp.ok) {
        const data = await resp.json();
        if (txtAgentStatus) txtAgentStatus.innerText = 'COMMANDER: SWARM DISPATCHED';
        syncServer();
      }
    } catch (err) {
      console.warn('Agent command dispatch error:', err);
    } finally {
      if (btnAgentDispatch) btnAgentDispatch.disabled = false;
    }
  }

  if (btnAgentDispatch) {
    btnAgentDispatch.addEventListener('click', () => {
      dispatchAgentPrompt(inputAgentPrompt.value);
    });
  }

  if (inputAgentPrompt) {
    inputAgentPrompt.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        dispatchAgentPrompt(inputAgentPrompt.value);
      }
    });
  }

  // Quick Scenario Preset Chips
  document.querySelectorAll('.btn-preset').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = btn.getAttribute('data-prompt');
      dispatchAgentPrompt(p);
    });
  });

  // Toggle Trace Collapsible View
  if (btnToggleTrace && agentTraceContainer) {
    btnToggleTrace.addEventListener('click', () => {
      const isCollapsed = agentTraceContainer.classList.toggle('collapsed');
      if (lblToggleTrace) lblToggleTrace.innerText = isCollapsed ? 'EXPAND LOG' : 'COLLAPSE LOG';
    });
  }

  // Military SITREP Modal Handlers
  if (btnOpenSitrep && modalSitrep) {
    btnOpenSitrep.addEventListener('click', async () => {
      modalSitrep.style.display = 'flex';
      if (sitrepContent) sitrepContent.innerText = 'Fetching live SITREP from RescuePilot Strands Agent...';
      try {
        const resp = await fetch('/api/agent/sitrep');
        if (resp.ok) {
          const data = await resp.json();
          if (sitrepContent) sitrepContent.innerText = data.sitrep_text || 'No SITREP available.';
        }
      } catch (e) {
        if (sitrepContent) sitrepContent.innerText = 'Error loading SITREP from agent.';
      }
    });
  }

  if (btnCloseSitrep && modalSitrep) {
    btnCloseSitrep.addEventListener('click', () => {
      modalSitrep.style.display = 'none';
    });
  }

  if (modalSitrep) {
    modalSitrep.addEventListener('click', e => {
      if (e.target === modalSitrep) modalSitrep.style.display = 'none';
    });
  }

  if (btnCopySitrep && sitrepContent) {
    btnCopySitrep.addEventListener('click', () => {
      navigator.clipboard.writeText(sitrepContent.innerText).then(() => {
        const orig = btnCopySitrep.innerHTML;
        btnCopySitrep.innerHTML = '<span class="icon">✅</span> COPIED TO CLIPBOARD!';
        setTimeout(() => { btnCopySitrep.innerHTML = orig; }, 2200);
      });
    });
  }

  // Scenario Selector
  selScenario.addEventListener('change', e => {
    sendCommand({ action: 'load_scenario', scenario: e.target.value });
  });

  // Canvas Pan & Zoom
  canvas.addEventListener('mousedown', e => {
    isDragging = true;
    dragStart = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
  });

  window.addEventListener('mousemove', e => {
    if (isDragging) {
      panOffset.x = e.clientX - dragStart.x;
      panOffset.y = e.clientY - dragStart.y;
    }
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  canvas.addEventListener('wheel', e => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    zoomLevel = Math.max(0.4, Math.min(3.5, zoomLevel * zoomFactor));
  });

  document.getElementById('btn-zoom-in').addEventListener('click', () => {
    zoomLevel = Math.min(3.5, zoomLevel * 1.2);
  });

  document.getElementById('btn-zoom-out').addEventListener('click', () => {
    zoomLevel = Math.max(0.4, zoomLevel / 1.2);
  });

  document.getElementById('btn-zoom-reset').addEventListener('click', () => {
    zoomLevel = 1.0;
    panOffset = { x: 0, y: 0 };
  });

})();
