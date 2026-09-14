"""MAVLink Output Bridge for Drone Smart Path.

Bridges high-level autonomous trajectory planning and swarm coordination to
industry-standard MAVLink v2 protocols, QGroundControl flight plans (.plan),
and Mission Planner waypoint files (.waypoints).
"""

import json
import math
import os
import socket
import struct
import time
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

# MAVLink Protocol Constants
MAVLINK_V2_MAGIC = 0xFD
MAV_CMD_NAV_WAYPOINT = 16
MAV_CMD_NAV_LOITER_TIME = 19
MAV_CMD_NAV_RETURN_TO_LAUNCH = 20
MAV_CMD_NAV_LAND = 21
MAV_CMD_NAV_TAKEOFF = 22

MAV_FRAME_LOCAL_NED = 1
MAV_FRAME_GLOBAL_RELATIVE_ALT = 3
MAV_FRAME_LOCAL_ENU = 4

# Message IDs
MSG_ID_HEARTBEAT = 0
MSG_ID_SET_POSITION_TARGET_LOCAL_NED = 84

# CRC-EXTRA seeds for MAVLink v2
CRC_EXTRA_HEARTBEAT = 50
CRC_EXTRA_SET_POSITION_TARGET_LOCAL_NED = 143


def crc16_accumulate(byte_val: int, crc: int) -> int:
    """Accumulate standard X.25 CRC-16 used by MAVLink."""
    byte_val = byte_val & 0xFF
    tmp = byte_val ^ (crc & 0xFF)
    tmp = (tmp ^ (tmp << 4)) & 0xFF
    return ((crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF


def calculate_mavlink_crc(header_and_payload: bytes, crc_extra: int) -> int:
    """Calculate MAVLink v2 CRC-16 including the message CRC_EXTRA byte."""
    crc = 0xFFFF
    for byte in header_and_payload:
        crc = crc16_accumulate(byte, crc)
    crc = crc16_accumulate(crc_extra, crc)
    return crc


class MAVLinkBridge:
    """Translates 3D trajectories and swarm paths to MAVLink telemetry and mission plans."""

    def __init__(
        self,
        origin_lat: float = 47.397742,
        origin_lon: float = 8.545594,
        origin_alt: float = 488.0,
        sys_id: int = 1,
        comp_id: int = 1,
    ):
        """
        Initialize MAVLink bridge.

        Args:
            origin_lat: Latitude of local coordinate origin (0, 0)
            origin_lon: Longitude of local coordinate origin (0, 0)
            origin_alt: Ground altitude MSL in meters
            sys_id: Default MAVLink System ID for the drone (1-255)
            comp_id: Default MAVLink Component ID (1 = Autopilot, 191 = Companion)
        """
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        self.origin_alt = origin_alt
        self.sys_id = sys_id
        self.comp_id = comp_id
        self.packet_sequence = 0

    # -------------------------------------------------------------------------
    # Coordinate Transformations (Local Metric <-> Geographic WGS-84)
    # -------------------------------------------------------------------------

    def local_to_lat_lon(self, x: float, y: float) -> Tuple[float, float]:
        """
        Convert local Cartesian coordinates (x=East, y=North) to WGS-84 (Lat, Lon).
        Uses flat-earth projection accurate for local UAS operational radius (< 50 km).
        """
        meters_per_deg_lat = 111139.0
        lat_rad = math.radians(self.origin_lat)
        meters_per_deg_lon = 111139.0 * math.cos(lat_rad)

        delta_lat = y / meters_per_deg_lat
        delta_lon = x / max(1e-6, meters_per_deg_lon)

        return (round(self.origin_lat + delta_lat, 7), round(self.origin_lon + delta_lon, 7))

    def lat_lon_to_local(self, lat: float, lon: float) -> Tuple[float, float]:
        """Convert WGS-84 (Lat, Lon) back to local (x=East, y=North) in meters."""
        meters_per_deg_lat = 111139.0
        lat_rad = math.radians(self.origin_lat)
        meters_per_deg_lon = 111139.0 * math.cos(lat_rad)

        y = (lat - self.origin_lat) * meters_per_deg_lat
        x = (lon - self.origin_lon) * meters_per_deg_lon
        return (round(x, 2), round(y, 2))

    # -------------------------------------------------------------------------
    # MAVLink Setpoint Extraction
    # -------------------------------------------------------------------------

    def trajectory_to_ned_setpoints(
        self,
        trajectory: Any,
        sys_id: Optional[int] = None,
        speed: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Convert a Trajectory or point list into MAVLink SET_POSITION_TARGET_LOCAL_NED setpoints.

        Args:
            trajectory: Trajectory instance or list of (x, y) tuples.
            sys_id: Drone MAVLink System ID (defaults to self.sys_id).
            speed: Cruise speed in m/s (defaults to trajectory speed or 5.0).

        Returns:
            List of dictionaries with NED coordinates and velocity targets.
        """
        system_id = sys_id or self.sys_id

        if hasattr(trajectory, "points"):
            points = trajectory.points
            alt = getattr(trajectory, "altitude", 10.0)
            nominal_speed = speed or getattr(trajectory, "speed", 5.0)
        elif isinstance(trajectory, list):
            points = trajectory
            alt = 10.0
            nominal_speed = speed or 5.0
        else:
            raise ValueError("Trajectory must have 'points' or be a list of tuples")

        setpoints = []
        for i, pt in enumerate(points):
            x_local, y_local = pt[0], pt[1]

            # In NED frame: North is +X, East is +Y, Down is +Z (Altitude is -Z)
            x_ned = float(y_local)
            y_ned = float(x_local)
            z_ned = -float(alt)

            # Estimate directional velocity vector
            if i < len(points) - 1:
                next_pt = points[i + 1]
                dx = next_pt[0] - x_local
                dy = next_pt[1] - y_local
                dist = math.hypot(dx, dy)
                if dist > 1e-3:
                    vx = float((dy / dist) * nominal_speed)
                    vy = float((dx / dist) * nominal_speed)
                else:
                    vx, vy = 0.0, 0.0
            else:
                vx, vy = 0.0, 0.0

            # Calculate target yaw angle from movement direction
            yaw = math.atan2(vy, vx) if (vx != 0 or vy != 0) else 0.0

            # Type mask: 0b0000110111000000 = 0x0DC0 (use pos + vel + yaw, ignore accel + yaw_rate)
            type_mask = 0x0DC0

            setpoints.append({
                "time_boot_ms": int(i * 1000),
                "target_system": system_id,
                "target_component": self.comp_id,
                "coordinate_frame": MAV_FRAME_LOCAL_NED,
                "type_mask": type_mask,
                "x": x_ned,
                "y": y_ned,
                "z": z_ned,
                "vx": vx,
                "vy": vy,
                "vz": 0.0,
                "afx": 0.0,
                "afy": 0.0,
                "afz": 0.0,
                "yaw": yaw,
                "yaw_rate": 0.0,
            })

        return setpoints

    # -------------------------------------------------------------------------
    # Standard MAVLink v2 Binary Packet Serialization
    # -------------------------------------------------------------------------

    def encode_mavlink_v2_packet(
        self,
        msg_id: int,
        payload: bytes,
        crc_extra: int,
        sys_id: Optional[int] = None,
        comp_id: Optional[int] = None,
    ) -> bytes:
        """Serialize payload into standard MAVLink v2 binary packet frame."""
        system_id = sys_id or self.sys_id
        component_id = comp_id or self.comp_id
        payload_len = len(payload)

        # MAVLink v2 header (10 bytes):
        # [magic=0xFD, len, incompat_flags, compat_flags, seq, sys_id, comp_id, msg_id(3 bytes)]
        header = struct.pack(
            "<BBBBBBBHB",
            MAVLINK_V2_MAGIC,
            payload_len,
            0,  # incompat_flags
            0,  # compat_flags
            self.packet_sequence & 0xFF,
            system_id & 0xFF,
            component_id & 0xFF,
            msg_id & 0xFFFF,
            (msg_id >> 16) & 0xFF,
        )
        self.packet_sequence = (self.packet_sequence + 1) % 256

        header_and_payload = header[1:] + payload
        crc = calculate_mavlink_crc(header_and_payload, crc_extra)
        checksum = struct.pack("<H", crc)

        return header + payload + checksum

    def encode_heartbeat(self, sys_id: Optional[int] = None) -> bytes:
        """Encode standard MAVLink HEARTBEAT (#0) packet."""
        # custom_mode(uint32), type(uint8), autopilot(uint8), base_mode(uint8), system_status(uint8), mavlink_version(uint8)
        payload = struct.pack("<IBBBBB", 0, 2, 12, 1, 4, 3)  # Quadrotor, PX4, CustomMode, Active
        return self.encode_mavlink_v2_packet(MSG_ID_HEARTBEAT, payload, CRC_EXTRA_HEARTBEAT, sys_id=sys_id)

    def encode_set_position_target_local_ned(self, sp: Dict[str, Any]) -> bytes:
        """Encode MAVLink SET_POSITION_TARGET_LOCAL_NED (#84) binary packet."""
        # Payload struct: time_boot_ms(uint32), x(f), y(f), z(f), vx(f), vy(f), vz(f), afx(f), afy(f), afz(f),
        # yaw(f), yaw_rate(f), type_mask(uint16), target_system(uint8), target_component(uint8), coordinate_frame(uint8)
        payload = struct.pack(
            "<IfffffffffffHBBB",
            sp.get("time_boot_ms", 0),
            sp["x"],
            sp["y"],
            sp["z"],
            sp.get("vx", 0.0),
            sp.get("vy", 0.0),
            sp.get("vz", 0.0),
            sp.get("afx", 0.0),
            sp.get("afy", 0.0),
            sp.get("afz", 0.0),
            sp.get("yaw", 0.0),
            sp.get("yaw_rate", 0.0),
            sp.get("type_mask", 0x0DC0),
            sp.get("target_system", self.sys_id),
            sp.get("target_component", self.comp_id),
            sp.get("coordinate_frame", MAV_FRAME_LOCAL_NED),
        )
        return self.encode_mavlink_v2_packet(
            MSG_ID_SET_POSITION_TARGET_LOCAL_NED,
            payload,
            CRC_EXTRA_SET_POSITION_TARGET_LOCAL_NED,
            sys_id=sp.get("target_system", self.sys_id),
        )

    def generate_packet_stream(
        self,
        trajectory: Any,
        sys_id: Optional[int] = None,
        include_heartbeat: bool = True,
    ) -> Generator[bytes, None, None]:
        """Yield real-time MAVLink v2 binary packet stream for a trajectory."""
        system_id = sys_id or self.sys_id
        if include_heartbeat:
            yield self.encode_heartbeat(sys_id=system_id)

        setpoints = self.trajectory_to_ned_setpoints(trajectory, sys_id=system_id)
        for sp in setpoints:
            yield self.encode_set_position_target_local_ned(sp)

    # -------------------------------------------------------------------------
    # QGroundControl .plan (JSON) Export
    # -------------------------------------------------------------------------

    def export_qgroundcontrol_plan(
        self,
        trajectory: Any,
        output_file: Optional[str] = None,
        takeoff_alt: float = 10.0,
        cruise_speed: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Export trajectory to standard QGroundControl JSON Mission Plan format (.plan).
        Directly loadable in QGroundControl Ground Control Station.
        """
        if hasattr(trajectory, "points"):
            points = trajectory.points
            alt = getattr(trajectory, "altitude", takeoff_alt)
        elif isinstance(trajectory, list):
            points = trajectory
            alt = takeoff_alt
        else:
            raise ValueError("Trajectory must have points or be a list")

        items = []

        # Item 1: Planned Takeoff
        first_pt = points[0] if points else (0, 0)
        first_lat, first_lon = self.local_to_lat_lon(first_pt[0], first_pt[1])
        items.append({
            "autoContinue": True,
            "command": MAV_CMD_NAV_TAKEOFF,
            "doJumpId": 1,
            "frame": MAV_FRAME_GLOBAL_RELATIVE_ALT,
            "params": [0, 0, 0, None, first_lat, first_lon, alt],
            "type": "SimpleItem",
        })

        # Subsequent Waypoints
        for i, pt in enumerate(points[1:], start=2):
            lat, lon = self.local_to_lat_lon(pt[0], pt[1])
            items.append({
                "autoContinue": True,
                "command": MAV_CMD_NAV_WAYPOINT,
                "doJumpId": i,
                "frame": MAV_FRAME_GLOBAL_RELATIVE_ALT,
                "params": [0, 0, 0, None, lat, lon, alt],
                "type": "SimpleItem",
            })

        plan_dict = {
            "fileType": "Plan",
            "geoFence": {"circles": [], "polygons": [], "version": 2},
            "groundStation": "QGroundControl",
            "mission": {
                "cruiseSpeed": float(cruise_speed),
                "firmwareType": 12,  # PX4 Autopilot
                "hoverSpeed": 2.0,
                "items": items,
                "plannedHomePosition": [self.origin_lat, self.origin_lon, self.origin_alt],
                "vehicleType": 2,  # Multi-Rotor
                "version": 2,
            },
            "rallyPoints": {"points": [], "version": 2},
            "version": 1,
        }

        if output_file:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(plan_dict, f, indent=2)

        return plan_dict

    # -------------------------------------------------------------------------
    # Mission Planner / QGroundControl WPL 110 (.waypoints) Export
    # -------------------------------------------------------------------------

    def export_wpl_waypoints(
        self,
        trajectory: Any,
        output_file: Optional[str] = None,
        alt: float = 10.0,
    ) -> str:
        """
        Export trajectory to standard QGC WPL 110 text format.
        Compatible with QGroundControl, Mission Planner, and PX4 SITL.
        """
        if hasattr(trajectory, "points"):
            points = trajectory.points
            flight_alt = getattr(trajectory, "altitude", alt)
        elif isinstance(trajectory, list):
            points = trajectory
            flight_alt = alt
        else:
            raise ValueError("Trajectory must have points or be a list")

        lines = ["QGC WPL 110"]

        # Line 0: Home coordinate
        lines.append(f"0\t1\t0\t{MAV_CMD_NAV_WAYPOINT}\t0\t0\t0\t0\t{self.origin_lat:.7f}\t{self.origin_lon:.7f}\t{self.origin_alt:.1f}\t1")

        # Line 1: Takeoff
        if points:
            t_lat, t_lon = self.local_to_lat_lon(points[0][0], points[0][1])
            lines.append(f"1\t0\t{MAV_FRAME_GLOBAL_RELATIVE_ALT}\t{MAV_CMD_NAV_TAKEOFF}\t0\t0\t0\t0\t{t_lat:.7f}\t{t_lon:.7f}\t{flight_alt:.1f}\t1")

        # Subsequent Waypoints
        for idx, pt in enumerate(points[1:], start=2):
            lat, lon = self.local_to_lat_lon(pt[0], pt[1])
            lines.append(f"{idx}\t0\t{MAV_FRAME_GLOBAL_RELATIVE_ALT}\t{MAV_CMD_NAV_WAYPOINT}\t0\t0\t0\t0\t{lat:.7f}\t{lon:.7f}\t{flight_alt:.1f}\t1")

        content = "\n".join(lines) + "\n"

        if output_file:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

        return content

    # -------------------------------------------------------------------------
    # Multi-Drone Swarm Flight Plan Generation
    # -------------------------------------------------------------------------

    def export_swarm_plans(
        self,
        base_trajectory: Any,
        formation_offsets: List[Tuple[float, float]],
        output_dir: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate synchronized QGroundControl flight plans for each drone in a swarm.

        Args:
            base_trajectory: Leader trajectory.
            formation_offsets: List of (x, y) relative offsets for each drone.
            output_dir: Optional directory to write .plan files (drone_1.plan, drone_2.plan, ...).

        Returns:
            List of plan dictionaries for all drones.
        """
        if hasattr(base_trajectory, "points"):
            base_pts = base_trajectory.points
            alt = getattr(base_trajectory, "altitude", 10.0)
        else:
            base_pts = base_trajectory
            alt = 10.0

        swarm_plans = []
        for i, offset in enumerate(formation_offsets, start=1):
            # Translate base trajectory points by formation offset
            offset_points = [(p[0] + offset[0], p[1] + offset[1]) for p in base_pts]

            out_path = os.path.join(output_dir, f"drone_{i}.plan") if output_dir else None
            plan = self.export_qgroundcontrol_plan(offset_points, output_file=out_path, takeoff_alt=alt)
            swarm_plans.append(plan)

        return swarm_plans

    # -------------------------------------------------------------------------
    # UDP Network Streaming (To QGroundControl / PX4 SITL)
    # -------------------------------------------------------------------------

    def broadcast_udp(
        self,
        packets: List[bytes],
        host: str = "127.0.0.1",
        port: int = 14550,
    ) -> int:
        """
        Send binary MAVLink packets over UDP socket to QGroundControl or autopilot port.

        Returns:
            Count of packets successfully sent.
        """
        sent_count = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            for pkt in packets:
                sock.sendto(pkt, (host, port))
                sent_count += 1
        finally:
            sock.close()
        return sent_count
