# -*- coding: utf-8 -*-
"""
DROS PX4 Execution Adapter.
Re-exports or wraps the MAVLink adapter targeting PX4 SITL / HIL endpoints.
"""

from drone.adapters.mavlink.mavlink_adapter import DroneExecutionAdapter

class PX4DroneAdapter(DroneExecutionAdapter):
    """Specialized PX4 execution adapter for DROS-VEP Lite."""
    def __init__(self, sitl_engine=None):
        super().__init__(sitl_engine=sitl_engine)
        self.target_firmware = "PX4 Autopilot v1.14"
