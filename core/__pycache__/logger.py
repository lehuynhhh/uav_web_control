import csv
import os
from datetime import datetime


class CSVLogger:
    def __init__(self, log_dir="../logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        self.telemetry_log_path = os.path.join(self.log_dir, "telemetry_log.csv")
        self.command_log_path = os.path.join(self.log_dir, "command_log.csv")

        self.init_telemetry_log()
        self.init_command_log()

    def init_telemetry_log(self):
        if not os.path.exists(self.telemetry_log_path):
            with open(self.telemetry_log_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "time",
                    "system_id",
                    "connected",
                    "armed",
                    "mode",
                    "lat",
                    "lon",
                    "alt",
                    "roll",
                    "pitch",
                    "yaw",
                    "vx",
                    "vy",
                    "vz",
                    "ground_speed",
                    "vertical_speed",
                    "battery_voltage",
                    "battery_remaining"
                ])

    def init_command_log(self):
        if not os.path.exists(self.command_log_path):
            with open(self.command_log_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "time",
                    "command",
                    "target_system",
                    "lat",
                    "lon",
                    "altitude",
                    "speed",
                    "ack",
                    "result",
                    "result_text"
                ])

    def log_telemetry(self, drone):
        vx = drone.get("vx") or 0
        vy = drone.get("vy") or 0
        vz = drone.get("vz") or 0

        ground_speed = (vx ** 2 + vy ** 2) ** 0.5
        vertical_speed = -vz

        with open(self.telemetry_log_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                drone.get("system_id"),
                drone.get("connected"),
                drone.get("armed"),
                drone.get("mode"),
                drone.get("lat"),
                drone.get("lon"),
                drone.get("alt"),
                drone.get("roll"),
                drone.get("pitch"),
                drone.get("yaw"),
                drone.get("vx"),
                drone.get("vy"),
                drone.get("vz"),
                ground_speed,
                vertical_speed,
                drone.get("battery_voltage"),
                drone.get("battery_remaining")
            ])

    def log_command(
        self,
        command,
        target_system=1,
        lat=None,
        lon=None,
        altitude=None,
        speed=None,
        result=None
    ):
        ack = None
        ack_result = None
        result_text = None

        if isinstance(result, dict):
            ack_data = result.get("ack")

            if isinstance(ack_data, dict):
                ack = ack_data.get("ack")
                ack_result = ack_data.get("result")
                result_text = ack_data.get("result_text")

        with open(self.command_log_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                command,
                target_system,
                lat,
                lon,
                altitude,
                speed,
                ack,
                ack_result,
                result_text
            ])