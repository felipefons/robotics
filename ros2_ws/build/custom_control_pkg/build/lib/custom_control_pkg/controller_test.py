#!/usr/bin/env python3
import math

class TestController:
    def __init__(self):
        self.start_time = None

    def compute_action(self, current_pos, target_pos, current_time):
        """
        Bypasses math entirely and outputs a constant rate vector to test override status.
        """
        # Format: [roll_rate, pitch_rate, yaw_rate, collective_thrust]
        # Command: No roll, no pitch, a steady yaw rotation (0.5 rad/s), and safe climb thrust (-0.42)
        roll_rate = 0.0
        pitch_rate = 0.0
        yaw_rate = 0.5
        collective_thrust = -0.65

        return [roll_rate, pitch_rate, yaw_rate, collective_thrust]