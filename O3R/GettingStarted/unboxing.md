# Unboxing

If you received the starter kit (default package), following document will help you unbox and start the O3R system.

If nobody tampered with your O3R package, you should have following hardware:
- Camera head 1
![HEAD](./resources/head.jpg "O3R - HEAD")
- Camera head 2
- VPU (Video Processing Unit)
![VPU](./resources/vpu.jpg "O3R - VPU")
- FPD cables to connect the head(s) to the VPU

You need a strong enough power source: 2.5A and 24V minimum.

1) First, connect the head(s) to the VPU;
![CONNECTION-OVERVIEW](./resources/connection_overview.png "Connections")
2) Connect power to the VPU - <font color=red>ATTENTION: PIN2 is power! PIN3 is ground</font>
3) Connect the ethernet cable (not included in the package)
4) Wait until you see the ethernet LED flashing before pinging/connecting to the VPU.

That's it about the hardware. Next step: software installation

## Network configuration
The default IP address of the VPU is 192.168.0.69. A good first step is to make sure you can connect to the VPU:


```python
ping 192.168.0.69
```

If you do not receive an answer from the camera, you can try to adjust your network settings. Your laptop's IP should be within the same subnet's IP-range (for instance, 192.168.0.10).

## Software installation

_Note: We recommend for testing purposes to install the ifmO3r package in an clean python environment first. You can use_ `python -m venv "venv-name"` _to create a new virtual environment.

The ifm3d(ifm3dpy) is the go to library for ifm's 3D cameras. It provides the possibility to easily change parameters, get images and even more. The next steps will cover the general usage of ifm3dpy, and how to unlock the O3R capabilities. Because the ifm3dpy installation is easy and straight forward (no compiling needed), we focus on this installation. You can find tutorials for both ifm3dpy and ifm3d (C++) within the ifm3d library topic on [ifm3d](https://ifm.github.io/ifm3d-docs/index.html)

You can use the official PyPI package to install the ifm3dpy within your virtual environment:

```python
pip install ifm3dpy
```

## Check installation

Let's verify quickly that the installation worked! This command should display the list of packages installed in your environment:

```python
pip freeze
```

Open up a python shell with:

```python
python.exe
OR
./python.exe
```

Then try importing the package:

```python
import ifm3dpy
print(ifm3dpy.__version__)
>>>0.91.0
```

You can test the connection from VPU to camera head with following lines:

```python
from ifm3dpy import O3RCamera
o3r = O3RCamera()
config = o3r.get() #get the configuration saved on the VPU
```

Using the package `json` provides an easier tool for displaying JSON-Strings. The configuration from the VPU is always a JSON-String.

```python
import json
print(json.dumps(config, indent=4))
>>>{
    "device": {
        "clock": {
            "currentTime": 1581090739817663072
        },
        "diagnostic": {
            "temperatures": [],
            "upTime": 94000000000
        },
        "info": {
            "device": "0301",
            "deviceTreeBinaryBlob": "tegra186-quill-p3310-1000-c03-00-base.dtb",
            "features": {},
            "name": "TableTop2",
            "partNumber": "M03975",
            "productionState": "AA",
            "serialNumber": "000201234176",
            "vendor": "0001"
        },
        "network": {
            "authorized_keys": "",
            "ipAddressConfig": 0,
            "macEth0": "00:04:4B:EA:9F:D1",
            "macEth1": "00:02:01:23:41:76",
            "networkSpeed": 1000,
            "staticIPv4Address": "192.168.0.69",
            "staticIPv4Gateway": "192.168.0.201",
            "staticIPv4SubNetMask": "255.255.255.0",
            "useDHCP": false
        },
        "state": {
            "errorMessage": "",
            "errorNumber": ""
        },
        "swVersion": {
            "kernel": "4.9.140-l4t-r32.4+gc35f5eb9d1d9",
            "l4t": "r32.4.3",
            "os": "0.13.13-221",
            "schema": "v0.1.0",
            "swu": "0.15.12"
        }
    },
    "ports": {
        "port0": {
            "acquisition": {
                "framerate": 10.0,
                "version": {
                    "major": 0,
                    "minor": 0,
                    "patch": 0
                }
            },
            "data": {
                "algoDebugConfig": {},
                "availablePCICOutput": [],
                "pcicTCPPort": 50010
            },
            "info": {
                "device": "2301",
                "deviceTreeBinaryBlobOverlay": "001-ov9782.dtbo",
                "features": {
                    "fov": {
                        "horizontal": 127,
                        "vertical": 80
                    },
                    "resolution": {
                        "height": 800,
                        "width": 1280
                    },
                    "type": "2D"
                },
                "name": "",
                "partNumber": "M03976",
                "productionState": "AA",
                "sensor": "OV9782",
                "sensorID": "OV9782_127x80_noIllu_Csample",
                "serialNumber": "000000000281",
                "vendor": "0001"
            },
            "mode": "experimental_autoexposure2D",
            "processing": {
                "extrinsicHeadToUser": {
                    "rotX": 0.0,
                    "rotY": 0.0,
                    "rotZ": 0.0,
                    "transX": 0.0,
                    "transY": 0.0,
                    "transZ": 0.0
                },
                "version": {
                    "major": 0,
                    "minor": 0,
                    "patch": 0
                }
            },
            "state": "RUN"
        },
        "port1": {
            "acquisition": {
                "framerate": 10.0,
                "version": {
                    "major": 0,
                    "minor": 0,
                    "patch": 0
                }
            },
            "data": {
                "algoDebugConfig": {},
                "availablePCICOutput": [],
                "pcicTCPPort": 50011
            },
            "info": {
                "device": "2301",
                "deviceTreeBinaryBlobOverlay": "001-ov9782.dtbo",
                "features": {
                    "fov": {
                        "horizontal": 127,
                        "vertical": 80
                    },
                    "resolution": {
                        "height": 800,
                        "width": 1280
                    },
                    "type": "2D"
                },
                "name": "",
                "partNumber": "M03976",
                "productionState": "AA",
                "sensor": "OV9782",
                "sensorID": "OV9782_127x80_noIllu_Csample",
                "serialNumber": "000000000282",
                "vendor": "0001"
            },
            "mode": "experimental_autoexposure2D",
            "processing": {
                "extrinsicHeadToUser": {
                    "rotX": 0.0,
                    "rotY": 0.0,
                    "rotZ": 0.0,
                    "transX": 0.0,
                    "transY": 0.0,
                    "transZ": 0.0
                },
                "version": {
                    "major": 0,
                    "minor": 0,
                    "patch": 0
                }
            },
            "state": "RUN"
        },
        "port2": {
            "acquisition": {
                "exposureLong": 5000,
                "exposureShort": 400,
                "framerate": 10.0,
                "offset": 0.0,
                "version": {
                    "major": 0,
                    "minor": 0,
                    "patch": 0
                }
            },
            "data": {
                "algoDebugConfig": {},
                "availablePCICOutput": [],
                "pcicTCPPort": 50012
            },
            "info": {
                "device": "3201",
                "deviceTreeBinaryBlobOverlay": "001-irs2381c.dtbo",
                "features": {
                    "fov": {
                        "horizontal": 60,
                        "vertical": 45
                    },
                    "resolution": {
                        "height": 480,
                        "width": 640
                    },
                    "type": "3D"
                },
                "name": "",
                "partNumber": "M03976",
                "productionState": "AA",
                "sensor": "IRS2877C",
                "sensorID": "IRS2877C_60x45_4x2W_60x45_B1",
                "serialNumber": "000000000281",
                "vendor": "0001"
            },
            "mode": "standard_range4m",
            "processing": {
                "diParam": {
                    "anfFilterSizeDiv2": 2,
                    "enableDynamicSymmetry": true,
                    "enableStraylight": true,
                    "enableTemporalFilter": true,
                    "excessiveCorrectionThreshAmp": 0.3,
                    "excessiveCorrectionThreshDist": 0.08,
                    "maxDistNoise": 0.02,
                    "maxSymmetry": 0.4,
                    "medianSizeDiv2": 0,
                    "minAmplitude": 20.0,
                    "minReflectivity": 0.0,
                    "mixedPixelFilterMode": 1,
                    "mixedPixelThresholdRad": 0.15
                },
                "extrinsicHeadToUser": {
                    "rotX": 0.0,
                    "rotY": 0.0,
                    "rotZ": 0.0,
                    "transX": 0.0,
                    "transY": 0.0,
                    "transZ": 0.0
                },
                "version": {
                    "major": 0,
                    "minor": 0,
                    "patch": 0
                }
            },
            "state": "RUN"
        },
        "port3": {
            "acquisition": {
                "exposureLong": 5000,
                "exposureShort": 400,
                "framerate": 10.0,
                "offset": 0.0,
                "version": {
                    "major": 0,
                    "minor": 0,
                    "patch": 0
                }
            },
            "data": {
                "algoDebugConfig": {},
                "availablePCICOutput": [],
                "pcicTCPPort": 50013
            },
            "info": {
                "device": "3201",
                "deviceTreeBinaryBlobOverlay": "001-irs2381c.dtbo",
                "features": {
                    "fov": {
                        "horizontal": 60,
                        "vertical": 45
                    },
                    "resolution": {
                        "height": 480,
                        "width": 640
                    },
                    "type": "3D"
                },
                "name": "",
                "partNumber": "M03976",
                "productionState": "AA",
                "sensor": "IRS2877C",
                "sensorID": "IRS2877C_60x45_4x2W_60x45_B1",
                "serialNumber": "000000000282",
                "vendor": "0001"
            },
            "mode": "standard_range4m",
            "processing": {
                "diParam": {
                    "anfFilterSizeDiv2": 2,
                    "enableDynamicSymmetry": true,
                    "enableStraylight": true,
                    "enableTemporalFilter": true,
                    "excessiveCorrectionThreshAmp": 0.3,
                    "excessiveCorrectionThreshDist": 0.08,
                    "maxDistNoise": 0.02,
                    "maxSymmetry": 0.4,
                    "medianSizeDiv2": 0,
                    "minAmplitude": 20.0,
                    "minReflectivity": 0.0,
                    "mixedPixelFilterMode": 1,
                    "mixedPixelThresholdRad": 0.15
                },
                "extrinsicHeadToUser": {
                    "rotX": 3.14,
                    "rotY": 1.8,
                    "rotZ": 0.0,
                    "transX": 0.2,
                    "transY": 0.0,
                    "transZ": 0.0
                },
                "version": {
                    "major": 0,
                    "minor": 0,
                    "patch": 0
                }
            },
            "state": "RUN"
        }
    }
}
```

