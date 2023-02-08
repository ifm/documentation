# How to handle verbose logging for Docker containers
By default Docker containers handle (verbose) logging in ways that is not suited well to space constrained systems, e.g. embedded devices.

There are a different options to reduce the chances of deadlocked systems because of (persistent) container logging:
1. If a (persistent) volume is mounted to a container, please be aware that the logs are persistent beyond the container live time. The data has to be cleaned up manually by the user.
2. [Docker logging drivers](#docker-logging-drivers)
3. Per application specific logging: see example for ROS(1) [below](#ros-1-logging-configuration-inside-container)

## Docker logging drivers
See the Docker documentation about logging drivers [here](https://docs.docker.com/config/containers/logging/configure/)

### Docker logging configuration
By default, no log-rotation is performed. As a result, log-files stored by the default json-file logging driver logging driver can cause a significant amount of disk space to be used for containers that generate much output, which can lead to disk space exhaustion.

Docker keeps the json-file logging driver (without log-rotation) as a default to remain backward compatibility with older versions of Docker, and for situations where Docker is used as runtime for Kubernetes.

For other situations, the “local” logging driver is recommended as it performs log-rotation by default, and uses a more efficient file format. Refer to the Configure the default logging driver section below to learn how to configure the “local” logging driver as a default, and the local file logging driver page for more details about the “local” logging driver.

### Run a docker container with logging driver configuration
The following example starts a container with log output in non-blocking mode and a 4 megabyte buffer:
```shell
docker run -it --log-opt mode=non-blocking --log-opt max-buffer-size=4m <IMAGE>
```

### Double check the docker logging configuration for a container
Check the configuration in a new shell:
```shell
$ docker inspect -f '{{.HostConfig.LogConfig}}' <CONTAINER>

{json-file map[max-buffer-size:4m mode:non-blocking]}
```

## ROS 1 logging configuration inside container
For details on how to set ROS specific logging, please see the details below [here](http://wiki.ros.org/rosconsole)

### Content of logging config file
Replace the content of the ROS logging config file with the following.
A change of the config file requires the user to source the setup.bash again: `source /opt/ros/$ROS_DISTRO/setup.bash`

$ROS_ROOT/config/rosconsole.config
```
#
#   rosconsole will find this file by default at $ROS_ROOT/config/rosconsole.config
#
#   You can define your own by e.g. copying this file and setting
#   ROSCONSOLE_CONFIG_FILE (in your environment) to point to the new file
#
log4j.logger.ros=WARN
log4j.logger.ros.roscpp.superdebug=WARN
```


### Content of logging config file: ifm3d-ros specific configuration
For a ifm3d-ros node specific configuration, please use the config below:
```
log4j.logger.ros=INFO
log4j.logger.ros.roscpp.superdebug=WARN
log4j.logger.ros.ifm3d_ros_driver=WARN
log4j.logger.ros.ifm3d_ros_examples=WARN
log4j.logger.ros.ifm3d_ros_msgs=WARN
```
