
## Sample builds
**NOTE: I think this document can wait until we have a better idea of the images that are officially available for the O3R, and have a table with proper links to images and dockerfiles. I'm not sure this is necessary or if the dockerhub will be sufficient.**

This document gathers information about the Dockerfiles and images officially supported by ifm, and the ones we recommend using for building applications deployable on the VPU.

*Note: Find further information and samples at the official [docker documentation](<https://docs.docker.com/>)*

### Dockerfile

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
