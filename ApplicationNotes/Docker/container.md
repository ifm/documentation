# Build and deploy a container from scratch

This application note will focus on building a container and deploy it on the VPU. We start building a small container first. This container will increase in size and complexity the further we go. We will use a python base image and install the ifm3d (ifm3dpy) library later on.

*For more detailed information, see [Building a VPU runnable container](../../GeneralDoc/docker.md)*

## Building a container

Every Docker container image is built by Docker using a Dockerfile. This is just a text file named `Dockerfile` without any file extension. It is case sensitive. You can use `docker build [path to Dockerfile]` to start the build process.

Our first container will use `arm64v8/python:3.9.6-slim-buster` as the base image. Let's build the first container with that base image.

Dockerfile:

```Docker
#arm64v8 is the pre-requisite for running the container on the VPU.
FROM arm64v8/python:3.9.6-slim-buster
```

Building:

```Docker
docker build . -t ifm3d
```

We use a tag to identify the image more easily later on.

Build process:

```bash
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker build . -t ifm3d
Sending build context to Docker daemon  2.048kB
Step 1/1 : FROM arm64v8/python:3.9.6-slim-buster
 ---> 4770e646d0be
Successfully built 4770e646d0be
Successfully tagged ifm3d:latest
```

If the build was successful, you should be able to use `docker image ls` to display all built images:

```bash
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker image ls
REPOSITORY                TAG                 IMAGE ID       CREATED         SIZE
ifm3d                     latest              4770e646d0be   5 weeks ago     108MB
```



## Run a container

*Note: To run a container build for other chip architecture than the host system, you need `qemu` for the virtualization/simulation of the different chip architecture.*

For further information see:

- [Docker multi-CPU architecture](<https://docs.docker.com/desktop/multi-arch/>)
- [NVIDIA container runtime using qemu](<https://github.com/NVIDIA/nvidia-docker/wiki/NVIDIA-Container-Runtime-on-Jetson#enabling-jetson-containers-on-an-x86-workstation-using-qemu>)

To run the container, we use `docker run`. Through several arguments, we can specify the run command. Right now, we want to start the container interactively (`-it`) and with a bash interface (`/bin/bash`), so we can play around inside the container.

```bash
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker run -it ifm3d /bin/bash
WARNING: The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
root@ee24eff3c797:/#
```

Now we are within the container. The warning tells us that the base image was build for arm64/aarch64 systems, however the host of the running container is based on amd64.

We should be able to ask for the python version and start a REPL:

```bash
root@ee24eff3c797:/# python --version
Python 3.9.6
```

```bash
root@ee24eff3c797:/# python
Python 3.9.6 (default, Jun 29 2021, 19:34:26)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> print("hello")
hello
>>>
```

## Save a container

The container is working, let's save it so we can copy/share/transfer it around. Docker already provides us with the right tool: `docker save`.

```bash
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker save ifm3d > ifm3d.tar
```

## Copy the container to the VPU

We can use `scp` to copy the saved container (.tar).

```bash
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ scp ifm3d.tar oem@192.168.0.69:/home/oem/
oem@192.168.0.69's password:
ifm3d.tar                                                                       100%  108MB  51.5MB/s   00:02
```

A public ssh key needs to be provided to the VPU first, before connecting as the `oem` user to the VPU. You can find more information about that [here](../../GeneralDoc/docker.md#ssh-connection)

## SSH to VPU

Through `ssh` we can connect to the VPU:

```bash
devoegse@Ubuntu:/etc/docker$ ssh oem@192.168.0.69
oem@192.168.0.69's password:
Last login: Fri Feb  7 16:59:46 2020 from 192.168.0.10
o3r-vpu-c0:~$
```

On the VPU, we need to `sync`, so we can be sure that the just uploaded file is saved:
```bash
o3r-vpu-c0:~$ sync
```

The `ls` command should show us the copied container:
```bash
o3r-vpu-c0:~$ ls
ifm3d.tar
```

## Load the container

To extract/load the container, use `docker load` on the VPU:

```bash
o3r-vpu-c0:~$ docker load < ifm3d.tar
Loaded image: ifm3d:latest
```

Again, `docker image ls` is a good way to check if the image was loaded successful:

```bash
o3r-vpu-c0:~$ docker image ls
REPOSITORY          TAG                 IMAGE ID            CREATED                  SIZE
ifm3d               latest              4770e646d0be        Less than a second ago   108MB
```

To run the container, follow the process from [run a container](#run-a-container)

## Increase the usability of the container

Until now, our container is not really useful. Let's update the container kernel, install python packages and create a user (security). To do that, we need to improve the Dockerfile:

Dockerfile:

```Docker
#arm64v8 is the pre-requisite for running the cotnainer on the VPU.
FROM arm64v8/python:3.9.6-slim-buster

#Security updates
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y upgrade

#Create and activate virtual environment. This is not needed right now, but useful for multistage builds
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Your normal pip installation, within the venv. We also update pip
RUN pip install -U pip && pip install numpy

#Due to security reasons, using a "user" is recommended
RUN useradd --create-home pythonuser
USER pythonuser

#Easier to debug the container if issues are happening
ENV PYTHONFAULTHANDLER=1
```

Build process:

```bash
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker build . -t ifm3d
Sending build context to Docker daemon  113.1MB
Step 1/9 : FROM arm64v8/python:3.9.6-slim-buster
 ---> 4770e646d0be
...
Step 6/9 : RUN pip install -U pip && pip install numpy
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in bb51c405bbdb
Requirement already satisfied: pip in /opt/venv/lib/python3.9/site-packages (21.1.3)
Collecting pip
  Downloading pip-21.2.2-py3-none-any.whl (1.6 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 21.1.3
    Uninstalling pip-21.1.3:
      Successfully uninstalled pip-21.1.3
Successfully installed pip-21.2.2
...
Step 9/9 : ENV PYTHONFAULTHANDLER=1
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 4ea430894bc7
Removing intermediate container 4ea430894bc7
 ---> 14db5d89303f
Successfully built 14db5d89303f
Successfully tagged ifm3d:latest
```

*Note: Due to easier readability, the build process output was shortened*

As you can see, the build process is far more detailed. There are several layers and `intermediate` container builds (for debugging). You can start the container with the typical commands and check if numpy was installed:

```bash
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker run -it ifm3d:latest /bin/bash
WARNING: The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
pythonuser@319eb5ea67e0:/$ pip freeze
numpy==1.21.1
```

## Install ifm3d into the container

`ifm3dpy` is the python binding for the ifm3D library. You can install/compile it from source to use it. The ifm does also provide  a docker image, which can be used on the VPU, containing the ifm3d and the ifm3dpy.

If you want to build the ifm3D from scratch, look at the official [ifm3d documentation](*insert link*).
The Dockerfile could look similar to this:

```Docker
FROM ubuntu:20.04 AS build

# if defined, we run unit tests when building ifm3d
ARG run_tests

# if you are running unit tests against a camera at
# a different IP, set that here.
ENV IFM3D_IP 192.168.0.69
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /home/ifm
RUN apt-get update && apt-get -y upgrade
RUN apt-get update && \
    apt-get install -y libboost-all-dev \
                       git \
                       libcurl4-openssl-dev \
                       libgtest-dev \
                       libgoogle-glog-dev \
                       libxmlrpc-c++8-dev \
                       libopencv-dev \
                       libpcl-dev \
                       libproj-dev \
                       python3-dev \
                       python3-pip \
                       build-essential \
                       coreutils \
                       findutils \
                       cmake \
                       locales \
                       ninja-build
RUN apt-get clean

# install python
RUN apt-get -y install --no-install-recommends build-essential \
    python3-dev

#install(Update) python packages and dependencies seperate - improves Docker caching etc.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# build pybind11 with cmake - but first clone from the official github repo
RUN git clone --branch v2.3.0 https://github.com/pybind/pybind11.git && \
    cd /home/ifm/pybind11 && \
    mkdir -p build && \
    cd build && \
    cmake -DPYBIND11_TEST=OFF .. && \
    make && \
    make install

# First clone ifm3d repo via username and personal access token into the cotnainer and than build the ifm3d
# this build include ifm3d pybind for a python access via pybind11
ARG IFM3D_CLONE_REPO
RUN mkdir src && \
    cd src && \
    git clone --branch o3r/main ${IFM3D_CLONE_REPO} && \
    cd ifm3d && \
    echo "Building from current branch" && \
    mkdir build && \
    cd build && \
    cmake -GNinja -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_MODULE_OPENCV=ON -DBUILD_MODULE_PCICCLIENT=ON -DBUILD_MODULE_PYBIND11=ON -DPYTHON_EXECUTABLE=/usr/bin/python3 .. && \
    ninja && \
    ninja package && \
    ninja repackage
RUN ls -1 /home/ifm/src/ifm3d/build/*.deb | grep -iv 'unspecified' | xargs dpkg -i

# multistage to reduce image size, hide secrets and add ifm user
FROM ubuntu:20.04

COPY --from=build /usr /usr

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y && apt-get clean
```

*Note: You should leverage the layering from Docker to improve the build speed if you need to build again. Qemu emulates a ARM64 CPU in software on a x86 System which is slow. In case you are planning to build large application from source please consider to run this on a ARM64 based host.*

Another, easier way, would be pulling the already existing docker image:

```bash
devoegse@Ubuntu:~/Git/documentation$ docker pull ifmrobotics/ifm3d:l4t-latest
l4t-latest: Pulling from ifmrobotics/ifm3d
...
Digest: sha256:91f53f8777c0c13d1ccdd56442bf9c11d37b8846239bca68ed43c19e2313fec6
Status: Downloaded newer image for ifmrobotics/ifm3d:l4t-latest
docker.io/ifmrobotics/ifm3d:l4t-latest
```

*Note: Due to easier readability, the pull process output was shortened*

Let's try the image and see, if we can connect to a (physical connected) VPU:

```bash
devoegse@Ubuntu:~/Git/documentation$ docker run -it ifmrobotics/ifm3d:l4t-latest
WARNING: The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
ifm@1f21eb1f98d2:/$ ifm3d dump
{
  "device": {
    "clock": {
      "currentTime": 1581111542490926304
```

If this is working, we can also try the ifm3dpy implementation:

```python
ifm@8a167fde9edc:/$ python3
Python 3.6.9 (default, Apr 18 2020, 01:56:04)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import ifm3dpy
>>> o3r = ifm3dpy.O3RCamera()
>>> o3r.to_json()
{'device': {'clock': {'currentTime':
```

## Building on top of the ifm base image

Now you want your own container, with your python script to run. Base your Dockerfile simply on the `ifmrobotics/ifm3d:l4t-latest` image:

```Dockerfile
FROM ifmrobotics/ifm3d:l4t-latest
```

You can include now your scripts etc. as you want.

Following the steps:

- [docker save ifm3d > ifm3d.tar](#save-a-container)
- [scp ifm3d.tar oem@192.168.0.69:/home/oem/](#copy-the-container-to-the-vpu)
- [docker load < ifm3d.tar](#load-the-container)
- [docker run -it ifm3d:latest /bin/bash](#run-a-container)

Should enable you to execute the ifm3d / ifm3dpy within the container, running on the VPU.
