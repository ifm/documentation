# Building a VPU runnable container

The VPU (Video Processing Unit) is based on an NVIDIA Jetson system (TX2), which is arm46/aarch64 based.
Building container without the right base image will therefore not run on the VPU. An arm64/aarch64 base image is needed. Please read carefully the instructions at the
<https://github.com/NVIDIA/nvidia-docker/wiki/NVIDIA-Container-Runtime-on-Jetson[Nvidia> GitHub repository]
for set-up instruction. For running an aarch64 container on a x86-64 host the section
<https://github.com/NVIDIA/nvidia-docker/wiki/NVIDIA-Container-Runtime-on-Jetson#running-or-building-a-container-on-x86-using-qemubinfmt_misc-is-failing[Running> or building a container on x86]
is highly recommended.

## Sample builds

*Note: You can find further information and samples at the official docker documentation <https://docs.docker.com/>*

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

NVIDIAs base image is a good starting point for building a container

```Docker
FROM nvcr.io/nvidia/l4t-base:r32.4.3
```

This base image is with ca. 631MB rather big, but also contains several examples
for CUDA etc.

### Python - python-slim-buster

A good base image for the TX2 for using Python could be:

```Docker
#arm64v8 is the pre-requisite for running the container on the VPU.
FROM arm64v8/python:3.9.6-slim-buster
```

This python base image is with less than 100MB rather small. It contains python3
with the default libraries.

## Build process

To build a container you use `docker build [path/to/Dockerfile]`. If you need tags (names) for your container, you would need to specify that within your docker build command. Please refer to the official docker documentation for deeper information.

```Docker
#The Dockerfile is located within the same directory
docker build .
```

*Note: For futher information about `docker build` refer to the official docker documentation <https://docs.docker.com/engine/reference/commandline/build/>*

### Proxy

Depending on the network infrastructure, docker might need the proxy information for building/updating the container.

```Docker
#$HTTP_PROXY & $HTTPS_PROXY are variables containing the proxy address. E.g.: HTTPS_PROXY=https//[PROXY ADDRESS]
docker image build --build-arg http_proxy=$HTTP_PROXY --build-arg https_proxy=$HTTPS_PROXY -t jupyter .
```

## Run the container

Using `docker run` for starting the container.

```Docker
#Start the container interactively
docker run -it ifm3d /bin/bash
```

*Note: Fur further information about `docker run`, refer to the official documentation <https://docs.docker.com/engine/reference/run/>*

## Saving a container

To save (and later share) a container, use `docker save`. This will save the container locally (e.g. tar file).

```Docker
docker save ifm3d > ifm3d.tar
```

## Load and start container

Reloading the content of a previously saved image

```Docker
docker load < ifm3d.tar
```

Start the docker container like on every other device:

```Docker
docker run ifm3d
```

# Deploying a container to the VPU

There are several ways for deploying a container. We are focusing on two:

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

It needs to be verified if the copy process worked. It is possible to connect via ssh to the VPU. The command `sync` should be used on the VPU after the copy process is done.

*Note: the oem user has no write right outside of his home directory. Therefore use `/home/oem/`. You can create your own folders with within the oem directory.*

To load start the container see [Link](#load-and-start-container)

## Local docker registry

Due to the fact that proxy servers are sometimes hard to deal with and that disk resources on the VPU is also limited, it might come handy to run a Docker registry in the local network.

### Create local Docker registry

The local Docker registry is created by using the container images provided by Docker itself and start/host them.
On the host system (not the VPU) activate a local Docker registry with following commands:

```Docker
docker pull registry:latest
# Start the registry and bind the container ports to the host ports
docker run -d -p 5000:5000 --name registry registry:latest
```

### Push a container to local registry

To push a container to the registry, it is recommended to first tag the image differently. E.g. if the registry is run on the localhost with port 5000, the image tag could be named:

```Docker
docker tag ifm3d localhost:5000/ifm3d
```

Use the normal push command for uploading to the local registry:

```Docker
docker push localhost:5000/ifm3d
```

*Note: A local registry might seem complicated tos tart with. If you want further ifnormation refer to the official documentation <https://docs.docker.com/registry/deploying/>*

### Pull a container from the local registry - host

If a local Docker registry is running, use `docker pull` to pull the image:

```Docker
docker pull localhost:5000/ifm3d
```

### Pull a container from the local registry - VPU

*Coming soon*

### Stop the registry

To stop the registry:

```Docker
docker container stop registry && docker container rm -v registry
```
