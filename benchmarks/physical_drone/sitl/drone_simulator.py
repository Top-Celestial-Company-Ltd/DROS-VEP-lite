# -*- coding: utf-8 -*-
"""
DROS Physical Drone Bench - Lightweight 3D Physics SITL Engine
Simulates drone dynamics (Altitude, Velocity, Motor State, Battery, Crash Detection).
"""

import time

class DronePhysicsState:
    def __init__(self, initial_altitude=15.0):
        self.altitude = initial_altitude # meters
        self.velocity_z = 0.0           # m/s (positive = up, negative = down)
        self.latitude = 25.0330         # Initial coordinate
        self.longitude = 121.5654
        self.armed = True
        self.motors_active = True
        self.flight_mode = "MISSION"    # MISSION, HOVER, RTH, CRASHED, LANDED
        self.battery_pct = 98.0
        self.gravity = 9.81
        self.crashed = False
        self.last_update = time.time()
        self.blackbox_log = []

    def step(self, dt=0.1):
        """Advance physics simulation by dt seconds"""
        if self.crashed or self.flight_mode == "LANDED":
            return

        if not self.armed or not self.motors_active:
            # Gravity takes over: free fall
            self.velocity_z -= self.gravity * dt
            self.altitude += self.velocity_z * dt
            if self.altitude <= 0.0:
                self.altitude = 0.0
                self.velocity_z = 0.0
                self.crashed = True
                self.flight_mode = "CRASHED"
                self.log_event("CRASH_EVENT", "Impact with ground due to unpowered free fall!")
        else:
            # Powered flight
            if self.flight_mode == "HOVER":
                self.velocity_z = 0.0
            elif self.flight_mode == "MISSION":
                self.velocity_z = 0.0
            elif self.flight_mode == "RTH":
                if self.altitude > 2.0:
                    self.altitude -= 1.0 * dt
                else:
                    self.altitude = 0.0
                    self.flight_mode = "LANDED"
                    self.motors_active = False
                    self.armed = False
                    self.log_event("LAND_EVENT", "Safe touchdown under RTH failsafe.")

        self.battery_pct -= 0.01 * dt

    def disarm(self):
        """Execute motor disarm"""
        self.armed = False
        self.motors_active = False
        self.log_event("MOTOR_DISARM", f"Motors cut at altitude {self.altitude:.2f}m")

    def update_waypoint(self, lat, lon, alt):
        """Update navigation target"""
        self.latitude = lat
        self.longitude = lon
        self.altitude = alt
        self.log_event("WAYPOINT_UPDATE", f"Target: ({lat:.4f}, {lon:.4f}, {alt:.1f}m)")

    def log_event(self, event_type, details):
        self.blackbox_log.append({
            "timestamp": time.time(),
            "type": event_type,
            "altitude": self.altitude,
            "mode": self.flight_mode,
            "details": details
        })
