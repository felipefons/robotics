#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy

# Import PX4 Message Types (Using VehicleRatesSetpoint instead of TrajectorySetpoint)
from px4_msgs.msg import VehicleOdometry, OffboardControlMode, VehicleRatesSetpoint, VehicleCommand

# Import your custom technique classes
from .controller_pid import PIDController
from .controller_lqr import LQRController
from .controller_test import TestController

class MasterControlRunner(Node):
    def __init__(self):
        super().__init__('master_control_runner')

        # --- 1. Parameters & Configuration ---
        self.declare_parameter('control_mode', 'pid')
        mode = self.get_parameter('control_mode').get_parameter_value().string_value
        self.get_logger().info(f"Initializing Master Runner in Pure RATE Control Mode [{mode.upper()}]")

        # Initialize the chosen controller backend module
        if mode == 'lqr':
            self.controller = LQRController()
        elif mode == 'test':
            self.controller = TestController()
        else:
            self.controller = PIDController() # Defaults to PID

        # Internal State tracking variables
        self.current_odom = None
        self.offboard_setpoint_counter = 0

        # --- 2. ROS 2 Quality of Service (QoS) Profile ---
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
            depth=1
        )

        # --- 3. Publishers & Subscribers ---
        self.odom_sub = self.create_subscription(VehicleOdometry, '/fmu/out/vehicle_odometry', self.odom_callback, qos_profile)
        
        self.offboard_mode_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.rates_pub = self.create_publisher(VehicleRatesSetpoint, '/fmu/in/vehicle_rates_setpoint', qos_profile)
        self.command_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos_profile)

        # --- 4. High-Frequency Main Loop Clock ---
        # 50Hz (every 0.02s) to maintain a continuous, stable offboard control link
        self.control_timer = self.create_timer(0.02, self.master_timer_callback)

    def odom_callback(self, msg: VehicleOdometry):
        """Updates internal feedback variables when a fresh telemetry packet arrives."""
        self.current_odom = msg

    def master_timer_callback(self):
        """Main periodic loop execution handling offboard sync and custom rate injections."""
        # Continuous heartbeat stream required by PX4 safety rules
        self.publish_offboard_control_mode()

        if self.offboard_setpoint_counter < 10:
            self.offboard_setpoint_counter += 1
            return

        # Arm and engage offboard mode once the stream warms up
        if self.offboard_setpoint_counter == 10:
            self.engage_offboard_mode()
            self.arm_vehicle()
            self.offboard_setpoint_counter += 1

        # Don't execute mathematical controls until we have state feedback
        if self.current_odom is None:
            self.get_logger().warn("Waiting for vehicle odometry feedback...", throttle_duration_sec=2.0)
            return

        # Define targets (Example: Hover point at origin, -5 meters altitude in NED)
        target_position = [0.0, 0.0, -5.0]
        current_position = [self.current_odom.position[0], self.current_odom.position[1], self.current_odom.position[2]]

        time_now = self.get_clock().now()

        # --- 5. Calculate Custom Control Efforts ---
        # Your custom files must return a list or array formatted as:
        # [roll_rate (rad/s), pitch_rate (rad/s), yaw_rate (rad/s), collective_thrust (0.0 to -1.0)]
        custom_outputs = self.controller.compute_action(current_position, target_position, time_now)

        # Safety Fallback: ensure we have an array with all 4 required dimensions
        if len(custom_outputs) != 4:
            self.get_logger().error(f"Controller output must return 4 elements. Got {len(custom_outputs)}. Defending vehicle...", throttle_duration_sec=1.0)
            custom_outputs = [0.0, 0.0, 0.0, -0.1] # Zero rotation rates, minimal safe throttle

        # --- 6. Publish directly to the high-frequency PX4 Rate Loop ---
        self.publish_vehicle_rates(custom_outputs)

    def publish_offboard_control_mode(self):
        msg = OffboardControlMode()
        msg.position = False
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = True   # CRITICAL: Bypasses higher-level loops, routing stream straight to rates loop
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_mode_pub.publish(msg)

    def publish_vehicle_rates(self, rates):
        msg = VehicleRatesSetpoint()
        msg.roll = float(rates[0])
        msg.pitch = float(rates[1])
        msg.yaw = float(rates[2])
        # Thrust body vector: Z index dictates upward acceleration inside the NED frame (0.0 to -1.0)
        msg.thrust_body = [0.0, 0.0, float(rates[3])]
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.rates_pub.publish(msg)

    def send_vehicle_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()
        msg.command = command
        msg.param1 = param1
        msg.param2 = param2
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.command_pub.publish(msg)

    def engage_offboard_mode(self):
        self.get_logger().info("Requesting Transition to PX4 Offboard Mode...")
        self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)

    def arm_vehicle(self):
        self.get_logger().info("Sending Safe System Arm Command Request...")
        self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)


def main(args=None):
    rclpy.init(args=args)
    runner = MasterControlRunner()
    try:
        rclpy.spin(runner)
    except KeyboardInterrupt:
        runner.get_logger().info("Master Control environment shutdown triggered gracefully.")
    finally:
        runner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()