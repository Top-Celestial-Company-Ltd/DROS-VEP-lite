# -*- coding: utf-8 -*-
"""
MAVLink / Serial Bridge & Actuator Proxy for Physical Drone.
Routes packets through DROS guard before dispatching to physical motors/SITL.
"""

from .dros_guard import DROSPhysicalGuard

class MAVLinkExecutionBridge:
    def __init__(self, drone_physics_sim, enable_dros=True):
        self.sim = drone_physics_sim
        self.enable_dros = enable_dros
        self.guard = DROSPhysicalGuard() if enable_dros else None

    def execute_command(self, role, cmd_name, params):
        """Execute MAVLink command (e.g. MAV_CMD_COMPONENT_ARM_DISARM, MAV_CMD_NAV_WAYPOINT)"""
        if self.enable_dros:
            allowed, reason, latency_ns = self.guard.verify_action(role, cmd_name, params)
            if not allowed:
                return {
                    "status": "DENIED",
                    "reason": reason,
                    "latency_ns": latency_ns,
                    "drone_state": self.sim.flight_mode
                }

        # If allowed (or DROS disabled under B0 bare mode), dispatch to physics engine
        if cmd_name == "CRITICAL_ARM_DISARM" and params.get("arm") == 0:
            self.sim.disarm()
        elif cmd_name == "WAYPOINT_NAVIGATE":
            self.sim.update_waypoint(params["lat"], params["lon"], params["altitude"])
        elif cmd_name == "RETURN_TO_HOME":
            self.sim.flight_mode = "RTH"

        return {
            "status": "EXECUTED",
            "reason": "OK",
            "drone_state": self.sim.flight_mode
        }
