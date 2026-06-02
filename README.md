# PX4 + Gazebo + ROS2 in Docker

In Fedora 44 + Gnome 50.1. Need docker already installed.

## Download and Run QGroundControl

Use AppImage is the fastes way.

[QGroundControl](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/getting_started/download_and_install.html)
## X11 / Wayland compatibility

Fedora 44 defaults to Wayland.

Gazebo GUI inside Docker works more reliably with X11 compatibility enabled. If your distro works in X11 `xorg-x11-xauth xhost` shouldn't be needed.

Install X11 utilities:

```bash
sudo dnf install xorg-x11-xauth xhost
```
Allow Docker GUI access:

```bash
xhost +local:docker
```

Then force Qt/X11 compatibility:

```bash
export QT_QPA_PLATFORM=xcb
```
You can add that to your `.bashrc`.

## Deploy the docker container

```bash
docker run --rm -it \
    --network=host \
    --env=DISPLAY \
    --env=QT_QPA_PLATFORM=xcb \
    --env=QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw,Z \
    -e PX4_SIM_MODEL=gz_x500 \
    -e PX4_GZ_WORLD=default \
    -e PX4_UXRCE_DDS_PORT=8888 \
    px4io/px4-sitl-gazebo:latest
```

## ROS2 container

# Build the container

```bash
docker build -f Dockerfile.ros2 -t px4-ros2-humble .
```

# Run the ROS2 container

```bash
docker run --rm -it \
    --name ROS2-humble \
    --network=host \
    px4-ros2-humble
```

# Start DDS agent

```bash
MicroXRCEAgent udp4 -p 8888
```

Then verify in another shell:

```bash
docker exec -it ROS2-humble bash
```

then:
```bash
ros2 topic list
```

You should see
```bash
/fmu/out/vehicle_odometry
/fmu/out/vehicle_status
/fmu/in/offboard_control_mode
```
## Deploy both containers with Docker Compose

Use the compose file in this repository:

```bash
docker compose up --build
```

If you want the PX4 interactive prompt, start the stack in the background and attach to the PX4 service:

```bash
docker compose up -d
docker compose attach px4
```

The compose file already keeps `tty` and `stdin_open` enabled for the PX4 service, but `docker compose up` itself is still log-oriented. Attaching to `px4` is the closest equivalent to the old `docker run -it` workflow.

This starts both services in one file:

* `px4`: PX4 + Gazebo with the GUI/X11 settings.
* `ros2`: the Humble workspace container, which starts `MicroXRCEAgent udp4 -p 8888`.

If you want a shell inside the ROS2 container while the agent is running, use:

```bash
docker compose exec ros2 bash
```

