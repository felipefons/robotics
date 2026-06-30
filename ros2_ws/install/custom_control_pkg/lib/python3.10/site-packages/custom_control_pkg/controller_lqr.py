#!/usr/bin/env python3
import numpy as np

class LQRController:
    def __init__(self):
        """
        State Vector Format Suggestion:
        X = [x, y, z, dx, dy, dz, roll, pitch, yaw]
        Control Vector Format:
        U = [roll_rate, pitch_rate, yaw_rate, collective_thrust]
        """
        # TODO: Define your dynamic system state matrices
        # self.A = np.matrix(...)
        # self.B = np.matrix(...)
        # self.Q = np.diag([...])
        # self.R = np.diag([...])

        # Pre-calculated Optimal Gain Matrix K shape placeholder:
        # 4 outputs (U) mapped against your state vector size (e.g., 6 or 9 states)
        self.K = np.zeros((4, 6)) 

    def compute_action(self, current_pos, target_pos, current_time):
        """
        Computes LQR control efforts and returns the 4 needed rate elements.
        
        :return: List [roll_rate, pitch_rate, yaw_rate, collective_thrust]
        """
        # 1. Build spatial error state vector
        state_error = np.array([
            current_pos[0] - target_pos[0], # X error
            current_pos[1] - target_pos[1], # Y error
            current_pos[2] - target_pos[2], # Z error
            0.0,                            # dx error placeholder
            0.0,                            # dy error placeholder
            0.0                             # dz error placeholder
        ])

        # 2. Optimal feedback matrix multiplication: U = -K * x
        u = -1.0 * np.dot(self.K, state_error)
        control_vector = u.flatten().tolist()

        # 3. Extract mapped variables out to rate format
        roll_rate  = control_vector[0]
        pitch_rate = control_vector[1]
        yaw_rate   = control_vector[2]
        
        # Base hover mix offset handling for the output vector
        base_hover_thrust = -0.35
        collective_thrust = base_hover_thrust + control_vector[3]
        collective_thrust = max(-0.70, min(-0.10, collective_thrust))

        return [roll_rate, pitch_rate, yaw_rate, collective_thrust]