# Build and deploy a container from scratch

**Note: The ifm3dTiny is deprecated and will be replaced by the ifm3d. As soon as the ifm3d is available, this document will be adapted**

This application note will focus on building a container and deploy it on the VPU. We start building a small container first. This container will increase in size and complexity the further we go. We will use a python base image and install the ifm3d (ifm3dTiny) library later on.

*For more detailed information, see [Building a VPU runnable container](../../GeneralDoc/docker.md)*

## Building a container

Every Docker container image is built by Docker using a Dockerfile. This is just a file named `Dockerfile` without any file extension. It is case sensitive. You can use `docker build [path to Dockerfile]` to start the build process.

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

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker build . -t ifm3d
Sending build context to Docker daemon  2.048kB
Step 1/1 : FROM arm64v8/python:3.9.6-slim-buster
 ---> 4770e646d0be
Successfully built 4770e646d0be
Successfully tagged ifm3d:latest
```

If the build was successful, you should be able to use `docker image ls` to display all built images:

```console
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

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker run -it ifm3d /bin/bash
WARNING: The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
root@ee24eff3c797:/#
```

Now we are within the container. The warning tells us that the base image was build for arm64/aarch64 systems, however the host of the running container is based on amd64.

We should be able to ask for the python version and start a REPL:

```console
root@ee24eff3c797:/# python --version
Python 3.9.6
```

```console
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

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker save ifm3d > ifm3d.tar
```

## Copy the container to the VPU

We can use `scp` to copy the saved container (.tar).

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ scp ifm3d.tar oem@192.168.0.69:/home/oem/
oem@192.168.0.69's password:
ifm3d.tar                                                                       100%  108MB  51.5MB/s   00:02
```

Use `oem` as the password.

## SSH to VPU

Through `ssh` we can connect to the VPU:

```console
devoegse@Ubuntu:/etc/docker$ ssh oem@192.168.0.69
oem@192.168.0.69's password:
Last login: Fri Feb  7 16:59:46 2020 from 192.168.0.10
o3r-vpu-c0:~$
```

On the VPU, we need to `sync`, so we can be sure that the just uploaded file is saved:
```console
o3r-vpu-c0:~$ sync
```

The `ls` command should show us the copied container:
```console
o3r-vpu-c0:~$ ls
ifm3d.tar
```

## Load the container

To extract/load the container, use `docker load` on the VPU:

```console
o3r-vpu-c0:~$ docker load < ifm3d.tar
Loaded image: ifm3d:latest
```

Again, `docker image ls` is a good way to check if the image was loaded successful:

```console
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

```console
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

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker run -it ifm3d:latest /bin/bash
WARNING: The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
pythonuser@319eb5ea67e0:/$ pip freeze
numpy==1.21.1
```

## Install ifm3dTiny into the container

The ifm3dTiny needs several libraries etc. to be build. To decrease the final size of the container, we can use a multistage build. The first stage is used for compiling and the second one for building the final image.

It is also recommended to use a requirements.txt file for the base pip installation. With this approach, you can use the magic of layering within the Dockerfile and improve the build speed drastically.

Here is the content of the requirements.txt:

```txt
setuptools
wheel
numpy >= 1.17.5
matplotlib >=3.3.3
h5py <= 3.1.0
```

The dockerfile should look like:

```Docker
#arm64v8 is the pre-requisite for running the container on the VPU.
FROM arm64v8/python:3.9.6-slim-buster as compile-image

#Security updates
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y upgrade

#For h5py, you need several libs and install it from source (arch)
#https://docs.h5py.org/en/stable/build.html#source-installation
RUN apt-get -y install --no-install-recommends build-essential \
    gcc \
    python-dev \
    software-properties-common \
    libhdf5-dev \
    pkg-config

#Create a virtual env for a multistage build.
#h5py needs gcc etc. to compile. This increases the image size. Using the venv
#can decrease the final image size.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

#Install(Update) python packages and dependencies separate from ifm3dTiny - improves Docker caching etc.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Use a build image for the smaller size
FROM arm64v8/python:3.9.6-slim-buster as build-image

#Install libhdf5 for h5py
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install --no-install-recommends libhdf5-103 && apt-get clean

#Copy the venv from the compile image and activate it
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

#Install latest ifm3dTiny version
RUN pip install --no-cache-dir ifmO3r==0.1.3

#Due to security reasons, using a "user" is recommended
RUN useradd --create-home pythonuser
USER pythonuser

#Easier to debug the container
ENV PYTHONFAULTHANDLER=1

#Start the repl (docker run -it) and import the ifm3dTiny directly
ENTRYPOINT [ "python3.9", "-i", "-c", "import ifmO3r.ifm3dTiny" ]

```

Here are parts of the build process:

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker build . -t ifm3d
Sending build context to Docker daemon  113.1MB
Step 1/19 : FROM arm64v8/python:3.9.6-slim-buster as compile-image
 ---> 4770e646d0be
...
Step 8/19 : RUN pip install --no-cache-dir -r requirements.txt
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 6011d62e8aca
...
Step 19/19 : ENTRYPOINT [ "python3.9", "-i", "-c", "import ifmO3r.ifm3dTiny" ]
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 8a0a246f8089
Removing intermediate container 8a0a246f8089
 ---> e1195e850523
Successfully built e1195e850523
Successfully tagged ifm3d:latest
```

*Note: Due to easier readability, the build process output was shortened*

The overall build process was about 30-40min - using and AMD Ryzen 7 PRO 4750U with Rad and 32GB RAM. Expect a similar building time on your side. You should leverage the layering from Docker to improve the build speed if you need to build again (especially h5py is taking about 95% of the build time).

*Note: Qemu emulates a ARM64 CPU in software on a x86 System which is slow. In case you are planning to build large application from source please consider to run this on a ARM64 based host.*

Following the steps:

- [docker save ifm3d > ifm3d.tar](#save-a-container)
- [scp ifm3d.tar oem@192.168.0.69:/home/oem/](#copy-the-container-to-the-vpu)
- [docker load < ifm3d.tar](#load-the-container)
- [docker run -it ifm3d:latest /bin/bash](#run-a-container)

You should be able to import the `ifm3dTiny` library.

```console
o3r-vpu-c0:~$ docker run -it ifm3d:latest /bin/bash
>>> import ifmO3r.ifm3dTiny
>>>
```
