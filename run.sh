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

# --- Launching the Architecture ---
echo "Booting up PX4 and ROS2 containers..."

# 1. Start the stack in the background (-d)
docker compose up --build -d

# 2. Wait for PX4 to boot and initialize its network ports
echo "Waiting for PX4 simulation to spin up..."
sleep 5 

# 3. Check if your qgroundcontrol shortcut exists and launch it
if command -v qgroundcontrol >/dev/null 2>&1; then
    echo "Launching QGroundControl..."
    # The '&' pushes it to the background so the script keeps running
    # 'disown' completely detaches it so it doesn't close when you quit the terminal
    qgroundcontrol >/dev/null 2>&1 & disown
else
    echo "Notice: 'qgroundcontrol' shortcut not found."
    echo "If it's named differently, launch it manually with: ~/.local/bin/YOUR_FILE_NAME"
fi

echo "--------------------------------------------------------"
echo "Stack deployed successfully!"
echo "- Gazebo and QGroundControl are opening up."
echo "- Entering live PX4 terminal interface below..."
echo "  (Press Ctrl+C to disconnect from terminal views safely)"
echo "--------------------------------------------------------"

# 4. Connect your keyboard safely to the interactive drone prompt
docker compose attach px4