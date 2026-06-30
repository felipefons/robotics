#!/bin/bash

# --- Universal X11 / Wayland GUI Configuration ---
echo "Configuring display permissions for Docker..."

if command -v xhost >/dev/null 2>&1; then
    xhost +local:root >/dev/null 2>&1
    xhost +local:docker >/dev/null 2>&1
else
    echo "Warning: 'xhost' utility not found."
fi

export DISPLAY=${DISPLAY:-:0}
export QT_X11_NO_MITSHM=1

if [ -n "$WAYLAND_DISPLAY" ]; then
    echo "Wayland environment detected. Enabling X11 compatibility bridge (xcb)."
    export QT_QPA_PLATFORM=xcb
fi

# --- Sync Custom Assets to the local PX4 Repo ---
echo "Syncing custom worlds and models to PX4 directory..."
mkdir -p ./PX4-Autopilot/Tools/simulation/gz/worlds
mkdir -p ./PX4-Autopilot/Tools/simulation/gz/models

# Copy your tracked custom assets safely into the PX4 folder structure
if [ -d "./custom_worlds" ]; then
    echo "-> Injecting custom worlds..."
    cp -r ./custom_worlds/. ./PX4-Autopilot/Tools/simulation/gz/worlds/
fi

if [ -d "./custom_models" ]; then
    echo "-> Injecting custom models..."
    cp -r ./custom_models/. ./PX4-Autopilot/Tools/simulation/gz/models/
fi

# --- Launching the Architecture ---
echo "Booting up PX4 and ROS2 containers..."

# ----------------------------------------------------------------------
# 1. Start the stack in the background (-d)
# ----------------------------------------------------------------------
docker compose down
docker compose up --build -d

# 2. Wait for PX4 to boot and initialize its network ports
echo "Waiting for PX4 simulation to spin up..."
sleep 12 

# ----------------------------------------------------------------------
# 3. Check if your qgroundcontrol shortcut exists and launch it
# ----------------------------------------------------------------------
if command -v qgroundcontrol >/dev/null 2>&1; then
    echo "Launching QGroundControl..."
    qgroundcontrol >/dev/null 2>&1 & disown
else
    echo "Notice: 'qgroundcontrol' shortcut not found."
fi

# ----------------------------------------------------------------------
# 4. Inject automatic environment sourcing into ROS2 profiles
# ----------------------------------------------------------------------
echo "Configuring interactive terminal environments..."
docker compose exec -d ros2 bash -c "grep -q 'install/setup.bash' ~/.bashrc || (echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc && echo 'if [ -f /root/ws/install/setup.bash ]; then source /root/ws/install/setup.bash; fi' >> ~/.bashrc && cp ~/.bashrc ~/.bash_profile)"

# ----------------------------------------------------------------------
# 5. Connect Current Terminal Directly to the PX4 Console
# ----------------------------------------------------------------------
echo "--------------------------------------------------------"
echo "Stack deployed! This terminal is now connecting to PX4."
echo "Open a SECOND terminal tab to run your ROS2 commands:"
echo "docker compose exec -it ros2 ros2 run custom_control_pkg run_bypass_test"
echo "--------------------------------------------------------"

# This replaces the current shell process with the live PX4 console interface
docker compose attach px4