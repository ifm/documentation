# Using the GPU on the VPU

## Using the GPU of the VPU

The VPU provides substantial GPU (Graphical Processing Unit) power to the user. The best way to experience this is using CUDA and the samples from NVIDIA. To do so, we are building a container with the sample files from NVIDIA, push it to the VPU and execute it. This, however is not enough. Docker is not using/accessing the GPU power if not specified. We need to activate this to via the right runtime.

## Dockerfile

The following Dockerfile builds the container with the samples from NVIDIA.
<https://github.com/NVIDIA/cuda-samples/tree/master/Samples/deviceQuery>

Dockerfile:

```Docker
# Base linux for tegra (l4t) amr64/aarch64 image
FROM nvcr.io/nvidia/l4t-base:r32.4.3 AS buildstage

# Install necessary updates + git (for cloning the nvidia samples). Tag v10.2 specifies the right commit. VPU runs CUDA 10.2
RUN apt-get update && apt-get install -y --no-install-recommends make g++ git && apt-get install ca-certificates -y
RUN git clone --depth 1 --branch v10.2 https://github.com/NVIDIA/cuda-samples.git /tmp/

# Change into the right directory and install/make the samples
WORKDIR /tmp/Samples/deviceQuery
RUN make clean && make

# Multistage build to reduce the image size on the platform
FROM nvcr.io/nvidia/l4t-base:r32.4.3

# Copy the samples from the buildstage into the final image
RUN mkdir -p /usr/local/bin
COPY --from=buildstage /tmp/Samples/deviceQuery/deviceQuery /usr/local/bin

# Execute the deviceQuery and check for CUDA support. Don't forget the runtime with the docker run command
CMD ["/usr/local/bin/deviceQuery"]

```

Building the cotnainer:

```console
devoegse@Ubuntu:~/Docker/vpu-container/jetson/32.4.3/cuda$ docker image build . -t cuda-samples
Sending build context to Docker daemon  875.5MB
Step 1/9 : FROM nvcr.io/nvidia/l4t-base:r32.4.3 AS buildstage
 ---> c93fc89026d9
Step 2/9 : RUN apt-get update && apt-get install -y --no-install-recommends make g++ git && apt-get install ca-certificates -y
 ---> Using cache
 ---> 30657757ffa3
Step 3/9 : RUN git clone --depth 1 --branch v10.2 https://github.com/NVIDIA/cuda-samples.git /tmp/
 ---> Using cache
 ---> 537ff54de38f
Step 4/9 : WORKDIR /tmp/Samples/deviceQuery
 ---> Using cache
 ---> d0cca3628e8a
Step 5/9 : RUN make clean && make
 ---> Using cache
 ---> a9a4fd5d584c
Step 6/9 : FROM nvcr.io/nvidia/l4t-base:r32.4.3
 ---> c93fc89026d9
Step 7/9 : RUN mkdir -p /usr/local/bin
 ---> Using cache
 ---> ee3758c5bfa7
Step 8/9 : COPY --from=buildstage /tmp/Samples/deviceQuery/deviceQuery /usr/local/bin
 ---> 9bde1743fa3b
Step 9/9 : CMD ["/usr/local/bin/deviceQuery"]
 ---> [Warning] The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64) and no specific platform was requested
 ---> Running in 2c872a8da689
Removing intermediate container 2c872a8da689
 ---> 6dc92449daaa
Successfully built 6dc92449daaa
Successfully tagged cuda-samples:latest
```

After building the container, you can follow the steps from the documentation to test the container on the VPU:
- [Save the container](../../GeneralDoc/docker.md#saving-a-container): ```$ docker save cuda-samples > cuda-samples.tar```
- [Transfer the container](../../GeneralDoc/docker.md#scp): ```$ scp cuda-samples.tar oem@192.168.0.69:/home/oem```
- [Load the container](../../GeneralDoc/docker.md#load-and-start-container): ```$ docker load < cuda-samples.tar```

Start the container with the NVIDIA runtime - `--runtime nvidia`, to get access to the GPU.

The output of the running container should look similar to this:

```console
o3r-vpu-c0:~$ docker run -it --runtime nvidia cuda-samples
/usr/local/bin/deviceQuery Starting...

 CUDA Device Query (Runtime API) version (CUDART static linking)

Detected 1 CUDA Capable device(s)

Device 0: "NVIDIA Tegra X2"
  CUDA Driver Version / Runtime Version          10.2 / 10.2
  CUDA Capability Major/Minor version number:    6.2
  Total amount of global memory:                 3829 MBytes (4014751744 bytes)
  ( 2) Multiprocessors, (128) CUDA Cores/MP:     256 CUDA Cores
  GPU Max Clock rate:                            1300 MHz (1.30 GHz)
  Memory Clock rate:                             1300 Mhz
  Memory Bus Width:                              128-bit
  L2 Cache Size:                                 524288 bytes
  Maximum Texture Dimension Size (x,y,z)         1D=(131072), 2D=(131072, 65536), 3D=(16384, 16384, 16384)
  Maximum Layered 1D Texture Size, (num) layers  1D=(32768), 2048 layers
  Maximum Layered 2D Texture Size, (num) layers  2D=(32768, 32768), 2048 layers
  Total amount of constant memory:               65536 bytes
  Total amount of shared memory per block:       49152 bytes
  Total number of registers available per block: 32768
  Warp size:                                     32
  Maximum number of threads per multiprocessor:  2048
  Maximum number of threads per block:           1024
  Max dimension size of a thread block (x,y,z): (1024, 1024, 64)
  Max dimension size of a grid size    (x,y,z): (2147483647, 65535, 65535)
  Maximum memory pitch:                          2147483647 bytes
  Texture alignment:                             512 bytes
  Concurrent copy and kernel execution:          Yes with 1 copy engine(s)
  Run time limit on kernels:                     No
  Integrated GPU sharing Host Memory:            Yes
  Support host page-locked memory mapping:       Yes
  Alignment requirement for Surfaces:            Yes
  Device has ECC support:                        Disabled
  Device supports Unified Addressing (UVA):      Yes
  Device supports Compute Preemption:            Yes
  Supports Cooperative Kernel Launch:            Yes
  Supports MultiDevice Co-op Kernel Launch:      Yes
  Device PCI Domain ID / Bus ID / location ID:   0 / 0 / 0
  Compute Mode:
     < Default (multiple host threads can use ::cudaSetDevice() with device simultaneously) >

deviceQuery, CUDA Driver = CUDART, CUDA Driver Version = 10.2, CUDA Runtime Version = 10.2, NumDevs = 1
Result = PASS
```

You can find more information about the runtime and `docker compose` for this usecase [here](../../GeneralDoc/docker.md# *insert link*)