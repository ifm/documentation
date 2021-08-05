# Building a VPU runnable container

The VPU (Video Processing Unit) is based on an NVIDIA Jetson system (TX2), which is arm46/aarch64 based.
Building container without the right base image will therefore not run on the VPU. An arm64/aarch64 base image is needed. Please read carefully the instructions at the
<https://github.com/NVIDIA/nvidia-docker/wiki/NVIDIA-Container-Runtime-on-Jetson[Nvidia> GitHub repository]
for set-up instruction. For running an aarch64 container on a x86-64 host the section
<https://github.com/NVIDIA/nvidia-docker/wiki/NVIDIA-Container-Runtime-on-Jetson#running-or-building-a-container-on-x86-using-qemubinfmt_misc-is-failing[Running> or building a container on x86]
is highly recommended.

## Sample builds

*Note: Find further information and samples at the official docker documentation <https://docs.docker.com/>*

### Dockerfile

A docker file contains all the necessary information for building a container image. Most of the Dockerfiles are starting with a base image, suited for the hardware the container might be deployed. In theory, it doesn't matter where the container is deployed. However, chip architecture (arm64/aarch64) needs to be considered.

#### Example - Dockerfile

*Note: This is a sample Dockerfile and is not optimized. Security, performance, etc. have been excluded for easier reading.*

```Docker
FROM nvcr.io/nvidia/l4t-base:r32.4.3 AS buildstage

RUN apt-get update && apt-get install -y --no-install-recommends make g++
COPY ./samples /tmp/samples

WORKDIR /tmp/samples/1_Utilities/deviceQuery
RUN make clean && make

# Multistage build to reduce the image size on the Jetson
FROM nvcr.io/nvidia/l4t-base:r32.4.3

RUN mkdir -p /usr/local/bin
COPY --from=buildstage /tmp/samples/1_Utilities/deviceQuery/deviceQuery /usr/local/bin

CMD ["/usr/local/bin/deviceQuery"]
```

### NVIDIA base image - l4t-base

NVIDIAs base image is a good starting point for building a container usable by the VPU.

```Docker
FROM nvcr.io/nvidia/l4t-base:r32.4.3
```

This base image is with ca. 631MB rather big, but also contains several examples for CUDA etc.

*Note: Different/higher versions than r32.4.3 might cause some features to not work or the container is not runnable at all on the VPU*

### Python - python-slim-buster

A good base image for the TX2 using Python 3:

```Docker
#arm64v8 is the pre-requisite for running the container on the VPU.
FROM arm64v8/python:3.9.6-slim-buster
```

This python base image is with less than 100MB rather small. It contains python3 with the default libraries.

## Build process

To build a container use `docker build [path/to/Dockerfile]`. If image tags (names) are needed, specify that within the docker build command.

```Docker
#The Dockerfile is located within the same directory
docker build .
```

*Note: For further information about `docker build` refer to the official docker documentation <https://docs.docker.com/engine/reference/commandline/build/>*

### Proxy

Depending on the network infrastructure, docker might need the proxy information for building/updating the container.

```Docker
#$HTTP_PROXY & $HTTPS_PROXY are variables containing the proxy address. E.g.: HTTPS_PROXY=https//[PROXY ADDRESS]
docker image build --build-arg http_proxy=$HTTP_PROXY --build-arg https_proxy=$HTTPS_PROXY -t jupyter .
```

## Run the container

Use `docker run` for starting the container.

```Docker
#Start the container interactively
docker run -it ifm3d /bin/bash
```

*Note: Fur further information about `docker run`, refer to the official documentation <https://docs.docker.com/engine/reference/run/>*

## Saving a container

To save (and later share) a container, use `docker save`. This will save the container locally (e.g. tar file).

```console
docker save ifm3d > ifm3d.tar
```

## Load and start container

Reloading the content of a previously saved image

```console
docker load < ifm3d.tar
```

Start the docker container like on every other device:

```console
docker run ifm3d
```

*Note: The image name might be different than the saved container name. After `docker load`, docker will show the name of the loaded image*

# Deploying a container to the VPU

There are several ways for deploying a container. This documetnation focuses on following two:

- Using `scp`
- Using a local docker registry

Every VPU has two users:

- root - ifm user with all rights
- oem - customer user

## SSH connection

To connect to the VPU use ssh and the configured IP address of the VPU:

`ssh oem@192.168.0.69`

Use `oem` as the user password.

## SCP

It is possible to upload/copy a saved container via scp to the VPU.

```Linux
# container name: ifm3d
scp ifm3d.tar oem@192.168.0.69:/home/oem
```

The system will ask for a password: `oem`

It needs to be verified if the copy process worked. The command `sync` should be used on the VPU after the copy process is done.

*Note: Use ssh to connect to the VPU - see [SSH conection](#ssh-connection)*

*Note: The `oem` user has no write rights outside of his home directory. Therefore use `/home/oem/` for saving files etc. It is possible to create folders within the oem directory.*

To load start the container see [Load and start a container](#load-and-start-container)

## Local docker registry

Due to the fact that proxy servers are sometimes hard to deal with and that disk resources on the VPU is also limited, it might come handy to run a Docker registry in the local network.

### Create local Docker registry

The local Docker registry is created by using the container images provided by Docker itself and start/host them.
On the host system (not the VPU) activate a local Docker registry with following commands:

```console
docker pull registry:latest
# Start the registry and bind the container ports to the host ports
docker run -d -p 5000:5000 --name registry registry:latest
```

*Note: A local registry might seem complicated to start with. For further information refer to the official documentation <https://docs.docker.com/registry/deploying/>*

### Push a container to local registry

To push a container to the registry, it is recommended to first tag the image differently. E.g. if the registry is run on the localhost with port 5000, the image tag could be named:

```Docker
docker tag ifm3d localhost:5000/ifm3d
```

Use the normal push command for uploading to the local registry:

```Docker
docker push localhost:5000/ifm3d
```

### Pull a container from the local registry - host

If a local Docker registry is running, use `docker pull` to pull the image:

```console
docker pull localhost:5000/ifm3d
```

### Pull a container from the local registry - VPU

*Coming soon*

### Stop the registry

To stop the registry:

```console
docker container stop registry && docker container rm -v registry
```

# Autostart container on the VPU

For auto starting container, `Docker compose` is used. The VPU already provides a service `.config/systemd/user/oem-dc@.service` which can be used for starting (autostart) a service. There is no need to change this service.

## Docker compose

Generate a sample directory and a `docker-compose.yml` file at following destination: `/usr/share/oem/docker/compose/`. E.g. `/usr/share/oem/docker/compose/jupyter/docker-compose.yml`

This file should contain the information for starting the container you need.

### Sample docker-compose.yml

Following `docker-compose.yml` file would create a service called `jupyter`, based on the image: `jupyter` and bind the container ports 8888 to the host port 8888 on start.

```yml
version: "3.3"
services:
    jupyter:
        image: jupyter
        ports:
            - 8888:8888
```

*Note: The Docker version on the VPU expects the docker-compose.yml to be either version 2.2 or 3.3. Fur further information refer to <https://docs.docker.com/compose/gettingstarted/>*

## Start the service

A `docker-compose.yml` can be started via `docker-compose up` within the `docker-compose.yml` directory. It is also possible to start the service with `systemd`:

```Linux
systemctl --user start oem-dc@jupyter
```

After some seconds, the service should have started and it is possible to get the status of this service:

```Linux
systemctl --user status oem-dc@jupyter
```

Another way of seeing all running container is `docker ps`.

## Auto start the service/container after an reboot of the VPU

To restart the container automatically, `enable` the service:

```Linux
systemctl --user enable oem-dc@jupyter
```

See [Start the service](#start-the-service) on how to start the container with a `docker-compose.yml file`
