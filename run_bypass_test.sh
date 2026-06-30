#!/bin/bash
# --- run_bypass_test.sh ---
# Automated shortcut utility to execute the rate control bypass node.

echo "Launching PX4 Rate Bypass Control Test Node inside Docker..."

# Execute the runtime directly inside the active ROS2 container
docker compose exec -it ros2 bash -c "
    source /opt/ros/humble/setup.bash && \
    source /root/ws/install/setup.bash && \
    ros2 run custom_control_pkg run_bypass_test --ros-args -p control_mode:=test
"