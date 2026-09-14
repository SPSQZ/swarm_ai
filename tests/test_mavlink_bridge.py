"""Tests for MAVLink Output Bridge."""

import json
import os
import tempfile

from interfaces.mavlink_bridge import (
    MAVLinkBridge,
    MAVLINK_V2_MAGIC,
    MSG_ID_HEARTBEAT,
    MSG_ID_SET_POSITION_TARGET_LOCAL_NED,
    calculate_mavlink_crc,
    CRC_EXTRA_HEARTBEAT,
)
from planner.generator import PathGenerator
from swarm.formation import FormationController


def test_coordinate_transformation_roundtrip():
    bridge = MAVLinkBridge(origin_lat=47.397742, origin_lon=8.545594)
    x_orig, y_orig = 50.0, -30.0

    lat, lon = bridge.local_to_lat_lon(x_orig, y_orig)
    assert isinstance(lat, float)
    assert isinstance(lon, float)

    x_back, y_back = bridge.lat_lon_to_local(lat, lon)
    assert abs(x_back - x_orig) < 0.5
    assert abs(y_back - y_orig) < 0.5


def test_trajectory_to_ned_setpoints():
    bridge = MAVLinkBridge()
    gen = PathGenerator()
    traj = gen.generate_straight(start=(0.0, 0.0), goal=(20.0, 40.0), altitude=12.0)

    setpoints = bridge.trajectory_to_ned_setpoints(traj, sys_id=2)
    assert len(setpoints) == 2

    sp0 = setpoints[0]
    assert sp0["target_system"] == 2
    assert sp0["x"] == 0.0  # North = y_local
    assert sp0["y"] == 0.0  # East = x_local
    assert sp0["z"] == -12.0  # NED Down = -altitude
    assert sp0["vx"] > 0
    assert sp0["vy"] > 0

    sp1 = setpoints[1]
    assert sp1["x"] == 40.0
    assert sp1["y"] == 20.0
    assert sp1["z"] == -12.0


def test_mavlink_v2_binary_heartbeat_packet():
    bridge = MAVLinkBridge(sys_id=1)
    packet = bridge.encode_heartbeat()

    # MAVLink v2 header is 10 bytes, heartbeat payload is 9 bytes, checksum is 2 bytes -> 21 bytes
    assert len(packet) == 21
    assert packet[0] == MAVLINK_V2_MAGIC
    assert packet[1] == 9  # Payload length
    assert packet[5] == 1  # System ID

    # Validate CRC
    header_and_payload = packet[1:19]
    expected_crc = calculate_mavlink_crc(header_and_payload, CRC_EXTRA_HEARTBEAT)
    packet_crc = int.from_bytes(packet[19:21], byteorder="little")
    assert expected_crc == packet_crc


def test_mavlink_v2_set_position_target_packet():
    bridge = MAVLinkBridge(sys_id=3)
    sp = {
        "time_boot_ms": 1500,
        "x": 10.0,
        "y": 20.0,
        "z": -15.0,
        "vx": 2.0,
        "vy": 3.0,
        "vz": 0.0,
        "yaw": 0.5,
        "target_system": 3,
    }
    packet = bridge.encode_set_position_target_local_ned(sp)

    # Header (10) + Payload (53) + CRC (2) = 65 bytes
    assert len(packet) == 65
    assert packet[0] == MAVLINK_V2_MAGIC
    assert packet[1] == 53  # Payload length
    assert packet[5] == 3   # System ID


def test_export_qgroundcontrol_plan():
    bridge = MAVLinkBridge()
    gen = PathGenerator()
    traj = gen.generate_turn(start=(0.0, 0.0), goal=(50.0, 50.0), altitude=15.0)

    with tempfile.TemporaryDirectory() as tmpdir:
        plan_path = os.path.join(tmpdir, "mission.plan")
        plan = bridge.export_qgroundcontrol_plan(traj, output_file=plan_path)

        assert plan["fileType"] == "Plan"
        assert "mission" in plan
        assert len(plan["mission"]["items"]) >= 2
        assert os.path.exists(plan_path)

        with open(plan_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        assert loaded_data["fileType"] == "Plan"


def test_export_wpl_waypoints():
    bridge = MAVLinkBridge()
    gen = PathGenerator()
    traj = gen.generate_straight(start=(0.0, 0.0), goal=(100.0, 100.0), altitude=20.0)

    with tempfile.TemporaryDirectory() as tmpdir:
        wpl_path = os.path.join(tmpdir, "test.waypoints")
        content = bridge.export_wpl_waypoints(traj, output_file=wpl_path)

        assert content.startswith("QGC WPL 110")
        assert os.path.exists(wpl_path)


def test_export_swarm_plans():
    bridge = MAVLinkBridge()
    gen = PathGenerator()
    traj = gen.generate_straight(start=(0.0, 0.0), goal=(30.0, 30.0), altitude=10.0)

    formation = FormationController(formation_type="wedge", spacing=3.0)
    offsets = formation.get_formation_offsets(num_drones=3)

    with tempfile.TemporaryDirectory() as tmpdir:
        plans = bridge.export_swarm_plans(traj, formation_offsets=offsets, output_dir=tmpdir)
        assert len(plans) == 3
        assert os.path.exists(os.path.join(tmpdir, "drone_1.plan"))
        assert os.path.exists(os.path.join(tmpdir, "drone_2.plan"))
        assert os.path.exists(os.path.join(tmpdir, "drone_3.plan"))


def test_packet_stream_generator():
    bridge = MAVLinkBridge()
    gen = PathGenerator()
    traj = gen.generate_candidates(start=(0.0, 0.0), goal=(10.0, 10.0))[0]

    packets = list(bridge.generate_packet_stream(traj, sys_id=1, include_heartbeat=True))
    assert len(packets) >= 2
    assert packets[0][0] == MAVLINK_V2_MAGIC
