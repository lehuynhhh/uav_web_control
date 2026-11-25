import math
from pymavlink import mavutil

class DroneCommand:
    def __init__(self, mav):
        self.mav = mav

    def arm(self, target_system=1, target_component=0):
        command = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM

        ack = self.mav.send_command_long_wait_ack(
            command,
            target_system=target_system,
            target_component=target_component,
            param1=1,
        )

        return {
            "status": "ARM command sent",
            "target_system": target_system,
            "ack": ack,
        }

    def force_arm(self, target_system=1, target_component=0):
        command = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM

        ack = self.mav.send_command_long_wait_ack(
            command,
            target_system=target_system,
            target_component=target_component,
            param1=1,
            param2=21196,
        )

        return {
            "status": "FORCE ARM command sent",
            "target_system": target_system,
            "ack": ack,
        }

    def disarm(self, target_system=1, target_component=0):
        command = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM

        ack = self.mav.send_command_long_wait_ack(
            command,
            target_system=target_system,
            target_component=target_component,
            param1=0,
        )

        return {
            "status": "DISARM command sent",
            "target_system": target_system,
            "ack": ack,
        }

    def takeoff(self, altitude=5, target_system=1, target_component=0):
        command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF

        nan = math.nan

        ack = self.mav.send_command_long_wait_ack(
            command,
            target_system=target_system,
            target_component=target_component,

            # MAV_CMD_NAV_TAKEOFF params:
            # param1: minimum pitch, not used for multicopter
            # param2: empty
            # param3: empty
            # param4: yaw angle
            # param5: latitude
            # param6: longitude
            # param7: altitude
            #
            # Use NaN for unused fields so PX4 uses current/default values.
            param1=nan,
            param2=nan,
            param3=nan,
            param4=nan,
            param5=nan,
            param6=nan,
            param7=float(altitude),
        )

        return {
            "status": "TAKEOFF command sent",
            "target_system": target_system,
            "altitude": altitude,
            "ack": ack,
        }
    
    def go_to_waypoint(self, lat, lon, altitude=5, speed=2, target_system=1, target_component=0):
        # Step 1: Change ground speed
        speed_ack = self.mav.send_command_long_wait_ack(
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
            target_system=target_system,
            target_component=target_component,
            param1=1,              # 1 = ground speed
            param2=float(speed),   # speed in m/s
            param3=-1,             # throttle unchanged
            param4=0,
            param5=0,
            param6=0,
            param7=0,
        )

        # Step 2: Reposition to waypoint
        waypoint_ack = self.mav.send_command_long_wait_ack(
            mavutil.mavlink.MAV_CMD_DO_REPOSITION,
            target_system=target_system,
            target_component=target_component,
            param1=-1,             # use current/default speed
            param2=0,
            param3=0,
            param4=math.nan,
            param5=float(lat),
            param6=float(lon),
            param7=float(altitude),
        )

        return {
            "status": "GO TO WAYPOINT command sent",
            "target_system": target_system,
            "lat": lat,
            "lon": lon,
            "altitude": altitude,
            "speed": speed,
            "speed_ack": speed_ack,
            "ack": waypoint_ack,
        }
    

    def land(self, target_system=1, target_component=0):
        command = mavutil.mavlink.MAV_CMD_NAV_LAND

        nan = math.nan

        ack = self.mav.send_command_long_wait_ack(
            command,
            target_system=target_system,
            target_component=target_component,
            param1=nan,
            param2=nan,
            param3=nan,
            param4=nan,
            param5=nan,
            param6=nan,
            param7=nan,
        )

        return {
            "status": "LAND command sent",
            "target_system": target_system,
            "ack": ack,
        }

    def rtl(self, target_system=1, target_component=0):
        command = mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH

        ack = self.mav.send_command_long_wait_ack(
            command,
            target_system=target_system,
            target_component=target_component,
        )

        return {
            "status": "RTL command sent",
            "target_system": target_system,
            "ack": ack,
        }