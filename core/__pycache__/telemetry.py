import math
import threading
import time
from pymavlink import mavutil


class TelemetryManager:
    def __init__(self, mav, drone_registry=None):
        self.mav = mav
        self.drone_registry = drone_registry
        self.running = False
        self.drones = {}

    def start(self):
        self.running = True
        thread = threading.Thread(target=self.read_loop, daemon=True)
        thread.start()

    def read_loop(self):
        while self.running:
            msg = self.mav.recv_msg()

            if msg is None:
                continue

            msg_type = msg.get_type()
            sysid = msg.get_srcSystem()
            compid = msg.get_srcComponent()

            # Ignore sysid 0 because it is not a vehicle.
            if sysid == 0:
                continue

            if sysid not in self.drones:
                self.drones[sysid] = self.default_drone_data(sysid, compid)

            self.drones[sysid]["last_update"] = time.strftime("%H:%M:%S")
            self.drones[sysid]["last_seen_ts"] = time.time()
            self.drones[sysid]["component_id"] = compid

            if msg_type == "HEARTBEAT":
                self.handle_heartbeat(sysid, msg)

            elif msg_type == "GLOBAL_POSITION_INT":
                self.handle_global_position(sysid, msg)

            elif msg_type == "ATTITUDE":
                self.handle_attitude(sysid, msg)

            elif msg_type == "SYS_STATUS":
                self.handle_sys_status(sysid, msg)

    def default_drone_data(self, sysid, compid):
        return {
            "system_id": sysid,
            "component_id": compid,
            "connected": True,
            "last_update": None,
            "last_seen_ts": time.time(),
            "armed": False,
            "mode": None,
            "lat": None,
            "lon": None,
            "alt": None,
            "roll": None,
            "pitch": None,
            "yaw": None,
            "vx": None,
            "vy": None,
            "vz": None,
            "battery_voltage": None,
            "battery_remaining": None,
        }

    def handle_heartbeat(self, sysid, msg):
        self.drones[sysid]["connected"] = True

        base_mode = msg.base_mode
        self.drones[sysid]["armed"] = bool(
            base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        )

        try:
            self.drones[sysid]["mode"] = mavutil.mode_string_v10(msg)
        except Exception:
            self.drones[sysid]["mode"] = "UNKNOWN"

        if self.drone_registry is not None:
            self.drone_registry.register_or_update_drone(sysid)

    def handle_global_position(self, sysid, msg):
        self.drones[sysid]["lat"] = msg.lat / 1e7
        self.drones[sysid]["lon"] = msg.lon / 1e7
        self.drones[sysid]["alt"] = msg.relative_alt / 1000.0
        self.drones[sysid]["vx"] = msg.vx / 100.0
        self.drones[sysid]["vy"] = msg.vy / 100.0
        self.drones[sysid]["vz"] = msg.vz / 100.0

    def handle_attitude(self, sysid, msg):
        self.drones[sysid]["roll"] = math.degrees(msg.roll)
        self.drones[sysid]["pitch"] = math.degrees(msg.pitch)
        self.drones[sysid]["yaw"] = math.degrees(msg.yaw)

    def handle_sys_status(self, sysid, msg):
        if msg.voltage_battery != 65535:
            self.drones[sysid]["battery_voltage"] = msg.voltage_battery / 1000.0

        if msg.battery_remaining != -1:
            self.drones[sysid]["battery_remaining"] = msg.battery_remaining

    def get_all_telemetry(self):
        now = time.time()
        online_drones = {}

        for sysid, drone in self.drones.items():
            last_seen_ts = drone.get("last_seen_ts", 0)

            if now - last_seen_ts <= 5:
                online_drones[sysid] = drone

        return online_drones

    def get_drone_telemetry(self, sysid):
        return self.drones.get(int(sysid))
