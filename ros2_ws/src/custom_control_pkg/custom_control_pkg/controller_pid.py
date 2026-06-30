#!/usr/bin/env python3

class PIDController:
    def __init__(self):
        # 3 Axes for Position Tracking Errors -> Outputs Desired Rates
        self.kp = [0.8, 0.8, 1.2]
        self.ki = [0.0, 0.0, 0.0]
        self.kd = [0.1, 0.1, 0.1]

        # Tracking variables for error calculus
        self.prev_error = [0.0, 0.0, 0.0]
        self.integral = [0.0, 0.0, 0.0]
        self.last_time = None

    def compute_action(self, current_pos, target_pos, current_time):
        """
        Processes outer-loop spatial errors and outputs inner-loop angular rates + thrust.
        
        :return: List [roll_rate (rad/s), pitch_rate (rad/s), yaw_rate (rad/s), thrust (0.0 to -1.0)]
        """
        if self.last_time is None:
            self.last_time = current_time
            return [0.0, 0.0, 0.0, -0.1]  # Safe default outputs (gentle low thrust)

        dt = (current_time - self.last_time).nanoseconds / 1e9
        if dt <= 0.0:
            return [0.0, 0.0, 0.0, -0.1]

        # Compute translation errors (Target - Current)
        error = [
            target_pos[0] - current_pos[0], # X error (translates to desired pitch)
            target_pos[1] - current_pos[1], # Y error (translates to desired roll)
            target_pos[2] - current_pos[2]  # Z error (translates to desired collective thrust)
        ]

        # --- PID Math Loop ---
        control_efforts = [0.0, 0.0, 0.0]
        for i in range(3):
            # Proportional
            p_term = self.kp[i] * error[i]
            
            # Integral
            self.integral[i] += error[i] * dt
            i_term = self.ki[i] * self.integral[i]
            
            # Derivative
            d_term = self.kd[i] * ((error[i] - self.prev_error[i]) / dt)
            
            control_efforts[i] = p_term + i_term + d_term

        # --- Map Control Efforts to Direct Rate Inputs ---
        # Note: In real flight dynamics, X/Y tracking errors map to pitch/roll angles,
        # which you will eventually differentiate into target rates. 
        # For this template, we map them directly as placeholder control demands.
        roll_rate  = control_efforts[1]  # Controlled via Y error
        pitch_rate = -control_efforts[0] # Controlled via X error (inverted in NED)
        yaw_rate   = 0.0                 # Keeping heading fixed for now
        
        # Base collective thrust baseline + Z axis feedback loop modification
        # Scaled between 0.0 (idle) and -1.0 (full skyward acceleration)
        base_hover_thrust = -0.35 
        collective_thrust = base_hover_thrust + control_efforts[2]
        
        # Clamp thrust output to absolute safe operating bounds
        collective_thrust = max(-0.70, min(-0.10, collective_thrust))

        # Save states for the next tick
        self.prev_error = error
        self.last_time = current_time

        return [roll_rate, pitch_rate, yaw_rate, collective_thrust]