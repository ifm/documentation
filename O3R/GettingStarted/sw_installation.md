# Software installation instructions

## Network configuration
The default IP address of the VPU is 192.168.0.69. A good first step is to make sure you can connect to the VPU:


```python
ping 192.168.0.69
```

If you do not receive an answer from the camera, you can try to adjust your network settings. Your laptop's IP should be within the same subnet's IP-range (for instance, 192.168.0.10).

## Software installation

The ifm3d (ifm3dpy, for python) is the go to library for ifm's 3D cameras. It provides the possibility to easily change parameters, get images and even more. The next steps will cover the installation steps and general usage of ifm3d, and how to unlock the O3R capabilities.

We provide multiple interfaces to use ifm 3D cameras. Follow the links below to find the relevant installation instructions:
- [ifm3dpy](ifm3d/doc/sphinx/content/installation_instructions/install_py:Python%20installation) (python installation)
- [ifm3d](ifm3d/doc/sphinx/content/installation_instructions/source_build:Installing%20ifm3d%20from%20source) (Linux c++ source build)
- [ifm3d for Windows](ifm3d/doc/sphinx/content/installation_instructions/windows:Building%20ifm3d%20from%20source%20on%20Windows) (Windows c++ source build)
- [ifm3d-ros](ROS/ifm3d-ros/README:Building%20and%20installing%20the%20software) (ifm3d for ROS, source build)
- [ifm3d-ros2](ROS/ifm3d-ros2/README:Building%20and%20Installing%20the%20Software) (ifm3d for ROS2, source build)
