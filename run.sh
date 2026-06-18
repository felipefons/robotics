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

# Copy your tracked custom assets into the ignored PX4 folder structure
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

# 1. Start the stack in the background (-d)
docker compose down
docker compose up --build -d

# 2. Wait for PX4 to boot and initialize its network ports
echo "Waiting for PX4 simulation to spin up..."
sleep 12 

# 3. Check if your qgroundcontrol shortcut exists and launch it
if command -v qgroundcontrol >/dev/null 2>&1; then
    echo "Launching QGroundControl..."
    qgroundcontrol >/dev/null 2>&1 & disown
else
    echo "Notice: 'qgroundcontrol' shortcut not found."
fi

echo "--------------------------------------------------------"
echo "Stack deployed successfully!"
echo "- Entering live PX4 terminal interface below..."
echo "--------------------------------------------------------"

# 4. Connect your keyboard safely to the interactive drone prompt
docker compose attach px4