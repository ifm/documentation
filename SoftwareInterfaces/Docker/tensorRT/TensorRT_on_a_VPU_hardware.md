# Using TensorRT

This document outlines the general process of AI inference acceleration with TensorRT on an OVP8xx device.

## Building a TensorRT container

There are two options:
- Use a base NVIDIA container and import the runtime libraries directly from the firmware. This is the preferred method that we will describe below.
- Use a complete NVIDIA container that includes the TensorRT libraries directly. This is not recommended since containers sizes will increase dramatically.

### NVIDIA base containers

NVIDIA provides L4T-based containers with TensorFlow that can be downloaded directly from [their containers catalog](https://ngc.nvidia.com/catalog/containers/nvidia:l4t-tensorflow).
TensorFlow should be used with the corresponding recommended version of JetPack.
The recommendations can be found on the [TensorFlow for Jetson website](https://docs.nvidia.com/deeplearning/frameworks/install-tf-jetson-platform-release-notes/tf-jetson-rel.html#tf-jetson-rel).

The L4T version on board the OVP80x (which contains the TX2 board) is [`r32.4.3`](https://developer.nvidia.com/embedded/linux-tegra-r32.4.3).
The supported JetPack version is `4.4`. Please see the official table on the [NVIDIA docs](https://docs.nvidia.com/deeplearning/frameworks/install-tf-jetson-platform-release-notes/tf-jetson-rel.html#tf-jetson-rel) for up to date compatibility information.

The underlying structure of the container loads the TensorRT libraries and is handled by NVIDIA and Docker - as long as the versions of the container and JetPack closely match.

#### Verify the functionality
For JetPack version 4.4 (L4T R32.4.3), the following versions are available:

```
l4t-tensorflow:r32.4.3-tf1.15-py3: TensorFlow 1.15
l4t-tensorflow:r32.4.3-tf2.2-py3: TensorFlow 2.2
```

First pull one of the `l4t-tensorflow` container tags from above, corresponding to the version of L4T that is installed on your Jetson and to the desired TensorFlow version. For example, if you are running the latest JetPack 4.4 (L4T R32.4.3) release and want to use TensorFlow 1.15, run:

```bash
docker pull nvcr.io/nvidia/l4t-tensorflow:r32.4.3-tf1.15-py3
```

Then, to start an interactive session in the container, run the following command:
```bash
docker run -it --rm --runtime nvidia --network host nvcr.io/nvidia/l4t-tensorflow:r32.4.3-tf1.15-py3
```
You should then be able to start a Python3 interpreter and import TensorFlow.

#### Mounting directories from the host
To mount scripts, data, etc. from your Jetson's filesystem to run inside the container, use Docker's `-v` flag when starting your Docker instance:
```bash
docker run -it --rm --runtime nvidia --network host -v /home/user/project:/location/in/container nvcr.io/nvidia/l4t-tensorflow:r32.4.3-tf1.15-py3
```


### Dockerfiles
#### NVIDIA base Dockerfiles

To access or modify the Dockerfiles and scripts used to build the NVIDIA containers, see this [GitHub repository](https://github.com/dusty-nv/jetson-containers).


#### ifm example Dockerfiles

The Dockerfiles for both the `o3r-l4t-base` and the `o3r-l4t-tensorrt` images can be found in the [`ifm3d-examples` repository on GitHub](https://github.com/ifm/ifm3d-examples).
The `o3r-l4t-base` image provides the bare minimum to install the NVIDIA packages via `apt-get`. It is a stripped down version of the NVIDIA `l4t-base` images with UI libraries removed.
The `o3r-l4t-tensorrt` image comes with the TensorRT examples from NVIDIA pre-installed and uses a multi stage Docker image build to show how to create smaller images without all the build tools pre-installed.

The Docker images are not distributed and need to be built locally.

## Using TensorRT in a container on the VPU

TensorRT applications can be memory-intensive. Here's how you can manage memory effectively:

1. Use `l4t-cuda-base` image and build TensorRT inside the container using Dockerfile. We recommend using Docker's multistage build feature to reduce the size in the final container.

2. Reduce the container mounting size by using [.dockerignore file](https://docs.docker.com/engine/reference/builder/#dockerignore-file).
Follow the [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) to minimize the number of layers and overall size.


Once TensorRT is installed on the VPU, you can proceed as follows:

1. Run TensorRT models using `trtexec` inside the `l4t-base` container. This container will copy TensorRT from the host.
2. `trtexec` runs the model, filing it with random data for testing purposes. This is a first indication whether the adapted model can be run on the final architecture.
3. Adapt the model for the final deployment architecture. This may involve updating the model based on its structure and the operators and layers used. Not all operators and model adaptations may be available in the OVP800 JetPack version. You may need to update your model on your development machine, export a new ONNX model with opset 11 operators, and adapt it again. This could be an iterative process.

### Adaptations for the OVP80x architecture

The model has to be exported and adapted to the final deployment architecture.
Refer to the [NVIDIA documentation for this process](https://docs.nvidia.com/deeplearning/tensorrt/quick-start-guide/index.html#basic-workflow). This adaptation must be done on the final deployment architecture. Compiling on similar architectures, like Jetson evaluation boards, will result in an incompatible instruction set for the OVP800 architecture.

We recommend exporting the neural network model to an ONNX model. Adapting the model for the deployment architecture may require updates. This could be an iterative process to get the model running on the final architecture. Update your model on your development machine, export a new ONNX model with opset 11 operators, and test this update in Docker.

For ONNX exports with opset 11 settings and further ONNX operator support, refer to the [official `onnx-tensorrt` documentation](https://github.com/onnx/onnx-tensorrt/blob/release/7.1/operators.md).


### Runtime inference cycle times
Adapting the model as described will result in a model with a specific runtime on the TX2 device. You may need to adjust for different model sizes and operations. Remember, the typical cycle time on a development machine may not accurately reflect the expected cycle times on OVP80x TX2 hardware.

## Examples
### YOLOv4 Tiny
This example demonstrates the benchmarking of the YOLOv4 Tiny Object Detection network using the TensorRT tool [`trtexec`](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html#trtexec) within a container. The example is applicable for L4T 32.5.1 and has been tested on a TX2 development board. Additional details for TX2 JetPack version 32.4.3 are forthcoming.

The model was trained on a different machine, converted into ONNX format and then copied to the board.
When starting the container, a directory with a model can be mounted using `-v` option.

To get the hardware and library details of the host, run:

```bash
jetsontx2@jetsontx2-desktop:~/for_container$ jetson_release
 - NVIDIA Jetson TX2
   * Jetpack 4.5.1 [L4T 32.5.1]
   * NV Power Mode: MAXP_CORE_ARM - Type: 3
   * jetson_stats.service: active
 - Libraries:
   * CUDA: 10.2.89
   * cuDNN: 8.0.0.180
   * TensorRT: 7.1.3.0
   * Visionworks: 1.6.0.501
   * OpenCV: 4.1.1 compiled CUDA: YES
   * VPI: ii libnvvpi1 1.0.15 arm64 NVIDIA Vision Programming Interface library
   * Vulkan: 1.2.70
```

### Deepstream-l4t

The Deepstream-l4t NGC container is used in this example.

1. Pull the Deepstream-l4t NGC container.
  ```bash
  $ docker pull nvcr.io/nvidia/deepstream-l4t:5.1-21.02-samples
  ```

2. Verify the successful pull by listing the Docker images.
	```bash
	$ docker image ls
	REPOSITORY                          TAG                         IMAGE ID             CREATED             SIZE
	nvcr.io/nvidia/deepstream-l4t       5.1-21.02-samples           0ff77669c10          6 months ago        2.72GB
	```

3. Start the container on the VPU: please replace the mounted volume directory with your directory of choice containing the ONNX model
   ```bash
   $ docker container run -it --rm --net=host --runtime nvidia -v /home/jetsontx2/for_container/:/home/dl_models nvcr.io/nvidia/deepstream-l4t:5.1-21.02-samples bash
    ```

4. In the container, navigate to `/home/dl_models directory` and run `trtexec` with the following command:
    ```bash
    $ /usr/src/tensorrt/bin/trtexec --onnx=/home/dl_models/yolov4tiny_relu_best_ops12_fp32.onnx --fp16 --explicitBatch=1
    ```

5. Optimal performance is achieved by using fp16 (floating point 16) precision.
    For TX2 board, the compute capability is 6.2 (that is SM62 architecture), which does not have INT8 feature.
    The output of trtexec for Yolov4 Tiny network and fp16 precision is as below:
    ```bash
    root@jetsontx2-desktop:/home/dl_models# /usr/src/tensorrt/bin/trtexec --onnx=/home/dl_models/yolov4tiny_relu_best_ops12_fp32.onnx --fp16 --explicitBatch=1
    &&&& RUNNING TensorRT.trtexec # /usr/src/tensorrt/bin/trtexec --onnx=/home/dl_models/yolov4tiny_relu_best_ops12_fp32.onnx --fp16 --explicitBatch=1
    [09/23/2021-10:20:45] [I] === Model Options ===
    [09/23/2021-10:20:45] [I] Format: ONNX
    [09/23/2021-10:20:45] [I] Model: /home/dl_models/yolov4tiny_relu_best_ops12_fp32.onnx
    [09/23/2021-10:20:45] [I] Output:
    [09/23/2021-10:20:45] [I] === Build Options ===
    [09/23/2021-10:20:45] [I] Max batch: explicit
    [09/23/2021-10:20:45] [I] Workspace: 16 MB
    [09/23/2021-10:20:45] [I] minTiming: 1
    [09/23/2021-10:20:45] [I] avgTiming: 8
    [09/23/2021-10:20:45] [I] Precision: FP32+FP16
    [09/23/2021-10:20:45] [I] Calibration:
    [09/23/2021-10:20:45] [I] Safe mode: Disabled
    [09/23/2021-10:20:45] [I] Save engine:
    [09/23/2021-10:20:45] [I] Load engine:
    [09/23/2021-10:20:45] [I] Builder Cache: Enabled
    [09/23/2021-10:20:45] [I] NVTX verbosity: 0
    [09/23/2021-10:20:45] [I] Inputs format: fp32:CHW
    [09/23/2021-10:20:45] [I] Outputs format: fp32:CHW
    [09/23/2021-10:20:45] [I] Input build shapes: model
    [09/23/2021-10:20:45] [I] Input calibration shapes: model
    [09/23/2021-10:20:45] [I] === System Options ===
    [09/23/2021-10:20:45] [I] Device: 0
    [09/23/2021-10:20:45] [I] DLACore:
    [09/23/2021-10:20:45] [I] Plugins:
    [09/23/2021-10:20:45] [I] === Inference Options ===
    [09/23/2021-10:20:45] [I] Batch: Explicit
    [09/23/2021-10:20:45] [I] Input inference shapes: model
    [09/23/2021-10:20:45] [I] Iterations: 10
    [09/23/2021-10:20:45] [I] Duration: 3s (+ 200ms warm up)
    [09/23/2021-10:20:45] [I] Sleep time: 0ms
    [09/23/2021-10:20:45] [I] Streams: 1
    [09/23/2021-10:20:45] [I] ExposeDMA: Disabled
    [09/23/2021-10:20:45] [I] Spin-wait: Disabled
    [09/23/2021-10:20:45] [I] Multithreading: Disabled
    [09/23/2021-10:20:45] [I] CUDA Graph: Disabled
    [09/23/2021-10:20:45] [I] Skip inference: Disabled
    [09/23/2021-10:20:45] [I] Inputs:
    [09/23/2021-10:20:45] [I] === Reporting Options ===
    [09/23/2021-10:20:45] [I] Verbose: Disabled
    [09/23/2021-10:20:45] [I] Averages: 10 inferences
    [09/23/2021-10:20:45] [I] Percentile: 99
    [09/23/2021-10:20:45] [I] Dump output: Disabled
    [09/23/2021-10:20:45] [I] Profile: Disabled
    [09/23/2021-10:20:45] [I] Export timing to JSON file:
    [09/23/2021-10:20:45] [I] Export output to JSON file:
    [09/23/2021-10:20:45] [I] Export profile to JSON file:
    [09/23/2021-10:20:45] [I]
    ----------------------------------------------------------------
    Input filename:   /home/dl_models/yolov4tiny_relu_best_ops12_fp32.onnx
    ONNX IR version:  0.0.6
    Opset version:    12
    Producer name:    pytorch
    Producer version: 1.8
    Domain:
    Model version:    0
    Doc string:
    ----------------------------------------------------------------
    [09/23/2021-10:20:47] [W] [TRT] onnx2trt_utils.cpp:220: Your ONNX model has been generated with INT64 weights, while TensorRT does not natively support INT64. Attempting to cast down to INT32.
    [09/23/2021-10:20:47] [W] [TRT] onnx2trt_utils.cpp:246: One or more weights outside the range of INT32 was clamped
    [09/23/2021-10:20:47] [W] [TRT] onnx2trt_utils.cpp:246: One or more weights outside the range of INT32 was clamped
    [09/23/2021-10:20:47] [W] [TRT] onnx2trt_utils.cpp:246: One or more weights outside the range of INT32 was clamped
    [09/23/2021-10:20:47] [W] [TRT] onnx2trt_utils.cpp:246: One or more weights outside the range of INT32 was clamped
    [09/23/2021-10:20:47] [W] [TRT] Output type must be INT32 for shape outputs
    [09/23/2021-10:20:56] [I] [TRT] Some tactics do not have sufficient workspace memory to run. Increasing workspace size may increase performance, please check verbose output.
    [09/23/2021-10:24:32] [I] [TRT] Detected 1 inputs and 6 output network tensors.
    [09/23/2021-10:24:33] [I] Starting inference threads
    [09/23/2021-10:24:36] [I] Warmup completed 0 queries over 200 ms
    [09/23/2021-10:24:36] [I] Timing trace has 0 queries over 3.01861 s
    [09/23/2021-10:24:36] [I] Trace averages of 10 runs:
    [09/23/2021-10:24:36] [I] Average on 10 runs - GPU latency: 11.6003 ms - Host latency: 11.7851 ms (end to end 11.8375 ms, enqueue 6.83557 ms)
    [09/23/2021-10:24:36] [I] Average on 10 runs - GPU latency: 11.0905 ms - Host latency: 11.2746 ms (end to end 11.2852 ms, enqueue 6.02471 ms)
    [09/23/2021-10:24:36] [I] Average on 10 runs - GPU latency: 11.0689 ms - Host latency: 11.2532 ms (end to end 11.2637 ms, enqueue 5.55458 ms)
    [09/23/2021-10:24:36] [I] Average on 10 runs - GPU latency: 11.1319 ms - Host latency: 11.3166 ms (end to end 11.3275 ms, enqueue 6.30752 ms)
    ```