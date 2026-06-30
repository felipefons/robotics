# Autonomous Drone Simulation (PX4 + ROS 2 + Gazebo)

This repository provides a containerized simulation environment for autonomous drone operations using PX4 Autopilot, ROS 2 Humble, and Gazebo Sim. The architecture isolates core frameworks while mounting custom workspace packages for rapid development.

## Prerequisites

Ensure your host machine has the following dependencies:

* **Ubuntu 22.04+**
* **Docker & Docker Compose V2**
* **NVIDIA Container Toolkit** (for hardware acceleration)
* **xhost utility** (for GUI/X11 rendering)

## Setup Instructions

### 1. Clone this Repository

```bash
git clone https://github.com/felipefons/robotics.git
cd robotics

```

### 2. Clone the PX4 Autopilot Dependency

```bash
git clone https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
git submodule update --init --recursive
cd ..

```

### 3. Configure Permissions

```bash
sudo chown -R $USER:$USER ./PX4-Autopilot
chmod +x run.sh

```

## How to Launch

Execute the orchestration script to configure your display environment, sync models, and boot the stack:

```bash
./run.sh

```

* **Interacting:** The script attaches your terminal to the simulation environment.
* **Disconnecting:** Press `Ctrl+C` to detach without shutting down the simulation.
* **Stopping:** Run `docker compose down` in your project root.


## How to run bypass test (optional)

Execute the bypass test script to see if the high-level Px4 PID controller is being bypassed:

```bash
./run_bypass_test.sh

```

* **Stopping:** Press `Ctrl+C` to stop the test without shutting down the simulation.


## How to run custom control techniques (WIP)

Execute the desired control technique script:

```bash
./run_bypass_test.sh

```

* **Stopping:** Press `Ctrl+C` to stop the test without shutting down the simulation.

## Development Notes

* **Workspace Sync:** `./ros2_ws` is mounted to `/root/ws`. Local changes in `src/` are reflected inside the container instantly.
* **Dependencies:** Add ROS 2 packages to `ros2_ws/src/` and run `colcon build` inside the container to compile.
* **Failsafe:** PX4 enters safe mode if the Offboard control link is lost. Ensure your scripts maintain a constant heartbeat.