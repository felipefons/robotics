Autonomous Drone Simulation (PX4 + ROS 2 + Gazebo)

This repository contains a containerized simulation environment for autonomous drone operations and computer vision tasks using PX4 Autopilot, ROS 2 Humble, and Gazebo Sim.

The architecture isolates core codebase frameworks while seamlessly mounting custom simulation assets and workspace packages.
Prerequisites

Before launching, ensure your host machine has the following dependencies installed:

    Ubuntu 22.04 (or compatible Linux distribution)

    Docker & Docker Compose V2

    NVIDIA Container Toolkit (if using hardware acceleration)

    xhost utility (for X11/Wayland GUI rendering)

Setup Instructions

Follow these steps to initialize the environment on your local machine:
1. Clone this Project Repository
Bash

git clone <https://github.com/felipefons/robotics.git>
cd your-project-root

2. Clone the PX4 Autopilot Dependency

Clone the official PX4 firmware and initialize its mandatory simulation submodules:
Bash

git clone https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
git submodule update --init --recursive
cd ..

3. Configure Permissions

Give your host user full read/write ownership over the external PX4 folder and make the deployment script executable:
Bash

sudo chown -R $USER:$USER ./PX4-Autopilot
chmod +x your_run_script.sh

How to Launch

Simply run the orchestration bash script. This script configures your local display environment (X11/Wayland), syncs the custom tracking worlds and models, boots up the containers, and launches QGroundControl:
Bash

./your_run_script.sh

    To interact with the drone: The script will automatically attach your terminal to the live interactive PX4 nsh prompt.

    To disconnect safely: Press Ctrl+C to detach from the terminal view without shutting down the simulation.

    To stop the entire stack: Run docker compose down in your project root.