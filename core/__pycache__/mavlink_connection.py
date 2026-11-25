import threading
import time
from pymavlink import mavutil


class MavlinkConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.master = None
        self.heartbeat_running = False
        self.io_lock = threading.Lock()

    def connect(self):
        print(f"Connecting MAVLink: {self.connection_string}")

        self.master = mavutil.mavlink_connection(
            self.connection_string,
            source_system=255,
            source_component=190
        )

        print("Sending GCS heartbeat...")
        for _ in range(5):
            self.master.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0,
                0,
                0
            )
            time.sleep(1)

        print("Waiting for heartbeat...")
        self.master.wait_heartbeat(timeout=10)

        print(
            f"Heartbeat received from system {self.master.target_system}, "
            f"component {self.master.target_component}"
        )

    def start_gcs_heartbeat(self):
        self.heartbeat_running = True
        thread = threading.Thread(target=self.gcs_heartbeat_loop, daemon=True)
        thread.start()
        print("GCS heartbeat started")

    def gcs_heartbeat_loop(self):
        while self.heartbeat_running:
            if self.master is not None:
                try:
                    self.master.mav.heartbeat_send(
                        mavutil.mavlink.MAV_TYPE_GCS,
                        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                        0,
                        0,
                        0
                    )
                except Exception:
                    pass

            time.sleep(1)

    def recv_msg(self):
        if self.master is None:
            return None

        with self.io_lock:
            return self.master.recv_match(blocking=True, timeout=1)

    def send_command_long(
        self,
        command,
        target_system=1,
        target_component=1,
        param1=0,
        param2=0,
        param3=0,
        param4=0,
        param5=0,
        param6=0,
        param7=0,
    ):
        if self.master is None:
            raise RuntimeError("MAVLink is not connected")

        self.master.mav.command_long_send(
            target_system,
            target_component,
            command,
            0,
            param1,
            param2,
            param3,
            param4,
            param5,
            param6,
            param7,
        )

    def send_command_long_wait_ack(
        self,
        command,
        target_system=1,
        target_component=1,
        param1=0,
        param2=0,
        param3=0,
        param4=0,
        param5=0,
        param6=0,
        param7=0,
        timeout=5,
    ):
        if self.master is None:
            raise RuntimeError("MAVLink is not connected")

        with self.io_lock:
            self.master.mav.command_long_send(
                target_system,
                target_component,
                command,
                0,
                param1,
                param2,
                param3,
                param4,
                param5,
                param6,
                param7,
            )

            end_time = time.time() + timeout

            while time.time() < end_time:
                msg = self.master.recv_match(
                    type="COMMAND_ACK",
                    blocking=True,
                    timeout=0.5
                )

                if msg is None:
                    continue

                if msg.command == command:
                    return {
                        "ack": True,
                        "command": msg.command,
                        "result": msg.result,
                        "result_text": self.command_result_text(msg.result)
                    }

            return {
                "ack": False,
                "message": "No COMMAND_ACK received"
            }

    def collect_statustext(self, duration=3):
        messages = []
        end_time = time.time() + duration

        with self.io_lock:
            while time.time() < end_time:
                msg = self.master.recv_match(
                    type="STATUSTEXT",
                    blocking=True,
                    timeout=0.5
                )

                if msg is not None:
                    messages.append(msg.text)

        return messages

    def command_result_text(self, result):
        result_map = {
            0: "ACCEPTED",
            1: "TEMPORARILY_REJECTED",
            2: "DENIED",
            3: "UNSUPPORTED",
            4: "FAILED",
            5: "IN_PROGRESS",
            6: "CANCELLED",
        }

        return result_map.get(result, f"UNKNOWN_RESULT_{result}")