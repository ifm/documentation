# Build and deploy a container from scratch

**Note: The ifm3dTiny is deprecated and will be replaced by the ifm3d. As soon as the ifm3d is available, this document will be adapted**

This application note will focus on building a container and deploy it on the VPU. We start building a small container first. This container will increase in size and complexity as further we go. We will use a python base image and install the ifm3d (ifm3dTiny) library later on.

*For more detailed information, see [Building a VPU runnable container](../../GeneralDoc/docker.md)*

## Building a container

Every Docker container image is build by Docker together with a Dockerfile. This is just a file named `Dockerfile` without any file extension. It is case sensitive. You can use `docker build [path to Dockerfile]` to start the build process.

Our first container will use `arm64v8/python:3.9.6-slim-buster` as the base image. Let's build the first container with that base image.

Dockerfile:

```Docker
#arm64v8 is the pre-requisite for running the cotnainer on the VPU.
FROM arm64v8/python:3.9.6-slim-buster
```

Building:

```Docker
docker build . -t ifm3d
```

We use a tag, to later on identify the image easier.

Build process:

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker build . -t ifm3d
Sending build context to Docker daemon  2.048kB
Step 1/1 : FROM arm64v8/python:3.9.6-slim-buster
 ---> 4770e646d0be
Successfully built 4770e646d0be
Successfully tagged ifm3d:latest
```

If the build was successful, you should be able to use `docker image ls` to display all build images:

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker image ls
REPOSITORY                TAG                 IMAGE ID       CREATED         SIZE
ifm3d                     latest              4770e646d0be   5 weeks ago     108MB
```

## Run a container

To run the container, we use `docker run`. Through several arguments, we can specify the run command. Right now, we want to start the container interactively (`-it`) and with the bash (`/bin/bash`). So we can play around inside the container.

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker run -it ifm3d /bin/bash
WARNING: The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
root@ee24eff3c797:/#
```

Now we are within the container. The warning tells us, that the base image was build for arm64/aarch64 systems, however the host of the running container is based on amd64.

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

Use `oem` as the password. On the VPU, we need to `sync`, so we can be sure that the just uploaded file is saved.

## SSH to VPU

Through `ssh` we can connect to the VPU:

```console
devoegse@Ubuntu:/etc/docker$ ssh oem@192.168.0.69
oem@192.168.0.69's password:
Last login: Fri Feb  7 16:59:46 2020 from 192.168.0.10
o3r-vpu-c0:~$
```

The `ls` command should show us the copied container:
```console
o3r-vpu-c0:~$ ls
ifm3d.tar
```

Don't forget and `sync` before we go on!

```console
o3r-vpu-c0:~$ sync
```

## Load the container

To extract/load the container, use `docker load` on the VPU:

```console
o3r-vpu-c0:~$ docker load < ifm3d.tar
Loaded image: ifm3d:latest
```

Again, `docker image ls` is a good way to prove if the image was loaded successful:

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
Step 2/9 : ARG DEBIAN_FRONTEND=noninteractive
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 4e4e01a99f77
Removing intermediate container 4e4e01a99f77
 ---> e07aa336261b
Step 3/9 : RUN apt-get -y update && apt-get -y upgrade
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in b460c02db7b7
Get:1 http://deb.debian.org/debian buster InRelease [122 kB]
Get:2 http://security.debian.org/debian-security buster/updates InRelease [65.4 kB]
Get:3 http://deb.debian.org/debian buster-updates InRelease [51.9 kB]
Get:4 http://deb.debian.org/debian buster/main arm64 Packages [7735 kB]
Get:5 http://security.debian.org/debian-security buster/updates/main arm64 Packages [293 kB]
Get:6 http://deb.debian.org/debian buster-updates/main arm64 Packages [14.5 kB]
Fetched 8282 kB in 7s (1196 kB/s)
Reading package lists...
Reading package lists...
Building dependency tree...
Reading state information...
Calculating upgrade...
The following packages will be upgraded:
  libsystemd0 libudev1
2 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
Need to get 460 kB of archives.
After this operation, 0 B of additional disk space will be used.
Get:1 http://security.debian.org/debian-security buster/updates/main arm64 libsystemd0 arm64 241-7~deb10u8 [314 kB]
Get:2 http://security.debian.org/debian-security buster/updates/main arm64 libudev1 arm64 241-7~deb10u8 [146 kB]
debconf: delaying package configuration, since apt-utils is not installed
Fetched 460 kB in 2s (273 kB/s)
(Reading database ... 6833 files and directories currently installed.)
Preparing to unpack .../libsystemd0_241-7~deb10u8_arm64.deb ...
Unpacking libsystemd0:arm64 (241-7~deb10u8) over (241-7~deb10u7) ...
Setting up libsystemd0:arm64 (241-7~deb10u8) ...
(Reading database ... 6833 files and directories currently installed.)
Preparing to unpack .../libudev1_241-7~deb10u8_arm64.deb ...
Unpacking libudev1:arm64 (241-7~deb10u8) over (241-7~deb10u7) ...
Setting up libudev1:arm64 (241-7~deb10u8) ...
Processing triggers for libc-bin (2.28-10) ...
Removing intermediate container b460c02db7b7
 ---> 7473db14948b
Step 4/9 : RUN python -m venv /opt/venv
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in beaa92fed55d
Removing intermediate container beaa92fed55d
 ---> 8539a93bdcde
Step 5/9 : ENV PATH="/opt/venv/bin:$PATH"
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 15892af8ae8d
Removing intermediate container 15892af8ae8d
 ---> afad479427b9
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
Collecting numpy
  Downloading numpy-1.21.1-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl (13.2 MB)
Installing collected packages: numpy
Successfully installed numpy-1.21.1
Removing intermediate container bb51c405bbdb
 ---> 816949368be8
Step 7/9 : RUN useradd --create-home pythonuser
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 47a37f8b0221
Removing intermediate container 47a37f8b0221
 ---> cc10008919f3
Step 8/9 : USER pythonuser
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in f169b3c9f567
Removing intermediate container f169b3c9f567
 ---> fade2722e04f
Step 9/9 : ENV PYTHONFAULTHANDLER=1
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 4ea430894bc7
Removing intermediate container 4ea430894bc7
 ---> 14db5d89303f
Successfully built 14db5d89303f
Successfully tagged ifm3d:latest
```

As you can see, the build process is far more detailed. There are several layers and `intermediate` container builds (for debugging). You can start the container with the typical commands and check, if numpy was installed:

```console
devoegse@Ubuntu:~/Git/documentation/ApplicationNotes/Docker/resources$ docker run -it ifm3d:latest /bin/bash
WARNING: The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
pythonuser@319eb5ea67e0:/$ pip freeze
numpy==1.21.1
```

## Install ifm3dTiny into the container

The ifm3dTiny needs several libraries etc. to be build. To decrease the final size of the container, we can use a multistage build. The first stages is used for the compiling and the second one for the building the final image.

It is also recommended, to use a requirements.txt file for the base pip installation. With this approach, you can use the magic of layering within the Dockerfile and improve the build speed drastically.

Here the content of the requirements.txt:

```txt
setuptools
wheel
numpy >= 1.17.5
matplotlib >=3.3.3
h5py <= 3.1.0
```

The dockerfile could look like:

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

Here parts of the build process:

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
Collecting h5py<=3.1.0
  Downloading h5py-3.1.0.tar.gz (371 kB)
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Installing backend dependencies: started
  Installing backend dependencies: finished with status 'done'
    Preparing wheel metadata: started
    Preparing wheel metadata: finished with status 'done'
...
Building wheels for collected packages: h5py
  Building wheel for h5py (PEP 517): started
  Building wheel for h5py (PEP 517): still running...
  Building wheel for h5py (PEP 517): finished with status 'done'
  Created wheel for h5py: filename=h5py-3.1.0-cp39-cp39-linux_aarch64.whl size=1237352 sha256=dc2cf923462babd07f0dec695bf507365efa576f180a07d7f5bd33d27970f917
  Stored in directory: /tmp/pip-ephem-wheel-cache-slh8yxv7/wheels/75/86/64/9b4e063eb07b8a72346cd87c93828072f5d2e3f837cc9e80b2
Successfully built h5py
Installing collected packages: six, python-dateutil, pyparsing, pillow, numpy, kiwisolver, cycler, wheel, matplotlib, h5py
Successfully installed cycler-0.10.0 h5py-3.1.0 kiwisolver-1.3.1 matplotlib-3.4.2 numpy-1.21.1 pillow-8.3.1 pyparsing-2.4.7 python-dateutil-2.8.2 six-1.16.0 wheel-0.36.2
WARNING: You are using pip version 21.1.3; however, version 21.2.2 is available.
You should consider upgrading via the '/opt/venv/bin/python -m pip install --upgrade pip' command.
Removing intermediate container 6011d62e8aca
 ---> 8a0779c76aea
Step 9/19 : FROM arm64v8/python:3.9.6-slim-buster as build-image
 ---> 4770e646d0be
Step 10/19 : ARG DEBIAN_FRONTEND=noninteractive
 ---> Using cache
 ---> e07aa336261b
Step 11/19 : RUN apt-get -y update && apt-get -y upgrade
 ---> Using cache
 ---> 7473db14948b
Step 12/19 : RUN apt-get -y install --no-install-recommends libhdf5-103 && apt-get clean
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 6a6933ee1b46
Reading package lists...
Building dependency tree...
Reading state information...
The following additional packages will be installed:
  libaec0 libgfortran5 libsz2
The following NEW packages will be installed:
  libaec0 libgfortran5 libhdf5-103 libsz2
0 upgraded, 4 newly installed, 0 to remove and 0 not upgraded.
Need to get 1491 kB of archives.
After this operation, 6187 kB of additional disk space will be used.
Get:1 http://deb.debian.org/debian buster/main arm64 libaec0 arm64 1.0.2-1 [18.8 kB]
Get:2 http://deb.debian.org/debian buster/main arm64 libgfortran5 arm64 8.3.0-6 [298 kB]
Get:3 http://deb.debian.org/debian buster/main arm64 libsz2 arm64 1.0.2-1 [6456 B]
Get:4 http://deb.debian.org/debian buster/main arm64 libhdf5-103 arm64 1.10.4+repack-10 [1168 kB]
debconf: delaying package configuration, since apt-utils is not installed
Fetched 1491 kB in 2s (965 kB/s)
Selecting previously unselected package libaec0:arm64.
(Reading database ... 6833 files and directories currently installed.)
Preparing to unpack .../libaec0_1.0.2-1_arm64.deb ...
Unpacking libaec0:arm64 (1.0.2-1) ...
Selecting previously unselected package libgfortran5:arm64.
Preparing to unpack .../libgfortran5_8.3.0-6_arm64.deb ...
Unpacking libgfortran5:arm64 (8.3.0-6) ...
Selecting previously unselected package libsz2:arm64.
Preparing to unpack .../libsz2_1.0.2-1_arm64.deb ...
Unpacking libsz2:arm64 (1.0.2-1) ...
Selecting previously unselected package libhdf5-103:arm64.
Preparing to unpack .../libhdf5-103_1.10.4+repack-10_arm64.deb ...
Unpacking libhdf5-103:arm64 (1.10.4+repack-10) ...
Setting up libaec0:arm64 (1.0.2-1) ...
Setting up libgfortran5:arm64 (8.3.0-6) ...
Setting up libsz2:arm64 (1.0.2-1) ...
Setting up libhdf5-103:arm64 (1.10.4+repack-10) ...
Processing triggers for libc-bin (2.28-10) ...
Removing intermediate container 6a6933ee1b46
 ---> bba304ca2076
...
Step 15/19 : RUN pip install --no-cache-dir ifmO3r==0.1.3
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 3033b2abaded
Collecting ifmO3r==0.1.3
  Downloading ifmO3r-0.1.3-py3-none-any.whl (56 kB)
...
Installing collected packages: ifmO3r
Successfully installed ifmO3r-0.1.3
WARNING: You are using pip version 21.1.3; however, version 21.2.2 is available.
...
Step 18/19 : ENV PYTHONFAULTHANDLER=1
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in c62457aae5a6
Removing intermediate container c62457aae5a6
 ---> 52a6eb094e24
Step 19/19 : ENTRYPOINT [ "python3.9", "-i", "-c", "import ifmO3r.ifm3dTiny" ]
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 8a0a246f8089
Removing intermediate container 8a0a246f8089
 ---> e1195e850523
Successfully built e1195e850523
Successfully tagged ifm3d:latest
```

The overall build process was about 30-40min. Expect similar or longer timings on your side. You should leverage the layering from Docker, to improve the build speed if you need to build again. Especially h5py is taking about 95% of the build time.

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
