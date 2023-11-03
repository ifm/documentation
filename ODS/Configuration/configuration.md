# Configuration

## ODS instance creation
A ODS app instance can be created using the regular ifm3d API `set` command.

The minimum ODS app application configuration object is suggested to be:
```JSON title="Minimal ODS app instance object"
{
    "applications": {
        "instances": {
            "app0": {
            "class": "ods",
            "configuration": {
                "activePorts": [
                    "port2",
                ],
                "port2": {},
                "vo": {
                    "voPorts": [
                        "port2",
                    ]
                }
            },
            "ports": [
                "port2",
                "port6"
            ],
            "state": "CONF"
            }
        }
    }
}
```
Note the application instance is created in `"state": "CONF"`. This is suggested for all application instances that are newly created.
Only once the application is fully configured is is set to live operation via a state change to `RUN` see the section [State](#state).



## ODS application parameter list

| Parameter   | Description |
 ------------ | ----------  |
| `name`      | Providing a custom name for the ODS application|
| `ports`     | The ports that can be used by the application (camera heads and IMU)|
| `state`     | The current app state and dependent camera hardware sates - "RUN" or "CONF"|
| `configuration/activePorts` | The list of camera ports that are active and being used by the application at one time. The number cannot exceed `maxNumSimultaneousCameras`. |
| `configuration/maxNumSimultaneousCameras` | The maximum number of cameras used simultaneously by ODS. This parameter requires a change to "CONF." |
| `grid/maxHeight`                          | Ceiling value above which all obstacles are ignored. Applies to the occupancy grid and all zones.|
| `grid/overhangingLoads` | A static region defined in the vehicle coordinate system which is excluded from the obstacle detection region (see [the overhanging loads documentation](../OverhangingLoads/overhanging_loads.md)). |
| `grid/temporalConsistencyConstraint` | Ensures that artifacts cause by dust particles are ignored (see [the dust mitigation documentation](../DustMitigation/dust_mitigation.md)). |
| `portX/acquisition/channelValue` | The camera channel value [-100, 100] used for a specific port to mitigate interference. Channel values should differ of at least 2.|
| `portX/negObst/enableNegativeObstacles` | Enable or disable the negative obstacle detection (see [the negative obstacle documentation](../NegativeObstacles/negative_obstacles.md)).|
| `portX/seg/minObjectHeight`                       | Minimum object height in [m], for example 0.025 [m]. This does not mean that any objects of this height will always be detected, but that objects below this height will be excluded from any detection. |
| `vo/voPorts`| Visual odometry - define a port which is the main camera stream for the visual odometry feature. Define multiple ports if a single reference port for visual odometry will not always be active, for example when switching between forward and backward looking cameras.|
| `zones`| Define the used protection zones - [See `ods zone definition` for a complete description](../Zones/zones.md)|

For more detail get the ODS application schema via the APIs `get_schema` method.
The application schema will be part of the overall schema once a ODS application has been created by the user.

:::{warning}
All connected heads have their own specific configuration. However, all heads referenced by the ODS are also configured by the application itself. **Only `channelValue` and `minObjectHeight` can be changed by the user and for each port separately**. The general configuration of ports (`{"ports":{"port2":...}}`) must not be changed by the user.
:::


## Channel value

The 3D imagers use the `TOF` - [TimeOfFlight](https://en.wikipedia.org/wiki/Time-of-flight_camera) - technology to estimate 3D data.
Due to this technical approach, it might happen that two heads are interfering with each other. Providing different channel values (that is, slightly different modulation frequencies), from -100 up to 100 channel value, for each head helps mitigate this issue. Pick channel values at least two digits apart of each other.

```JSON title="Channel value"
{
    "applications":{
        "instances":{
            "appX":{
                "configuration": {
                    "port2": {
                        "acquisition": {
                            "channelValue": -10
                            }
                    },
                    "port3": {
                        "acquisition": {
                            "channelValue": 10
                        }
                    }
                }
            }
        }
    }
}
```

## Minimum object height

It is possible to change the minimum object height to improve ODS for certain conditions. ODS can use several heads for detecting obstacles. The heads themselves might be different (opening angle of 105° or 60°), and the mounting position of the heads can vary. Therefore the `minObjectHeight` might be different per connected head. The height is provided in [m].
Increasing this value might prevent false positives caused by the floor and/or smaller objects on the ground.

:::{note}
    Note that this parameter is not the only factor defining whether an object will be detected or not: switching `minObjectHeight` to zero does not mean that every object will be detected. This is especially true for small objects on the floor, where point cloud artifacts are the most pronounced.
:::

```JSON title="minObjectHeight"
"configuration": {
    "port2": {
        "acquisition": {
            "seg": {
                "minObjectHeight": 0.025
            }
        }
    },
    "port3": {
        "acquisition": {
            "seg": {
                "minObjectHeight": 0.040
            }
        }
    }
}
```


## State

To activate/deactivate the application use the following definition:

- Active: "RUN"
- Inactive: "CONF"

:::{note}
To ensure that restarting the data stream is as quick as possible, we recommend keeping the application always in "RUN" state. For an inactive application, set the `activePorts` list to an empty list `[]`.
:::

## Extrinsic calibration

If no extrinsic calibration is provided, for example the extrinsic calibration parameters are set to their default values, the ODS application will not work!
This would mean the camera head is inside the floor (`transZ == 0`) and looking towards to ceiling, which is not a valid ODS extrinsic calibration use case.


:::{note}
Always forward all 6 extrinsic calibration values at the same time. You can edit the full configuration in a file and provide this file to the `ifm3d config` command.

```json
{
    "ports": {
        <port_number>: {
            "processing": {
                "extrinsicHeadToUser": {
                    "rotX": <rotX_value>,
                    "rotY": <rotY_value>,
                    "rotZ": <rotZ_value>,
                    "transX": <transX_value>,
                    "transY": <transY_value>,
                    "transZ": <transZ_value>
                }
            }
        }
    }
}
```
:::

:::{note}
The rotation is in rad (radians) - instead of 90°, you provide Pi/2
:::

For one camera, connected to port 2, facing forward (+x) with label up (+z) and shifted 20 cm vertically, the calibration can be set with:
```python
from ifm3dpy.device import O3R
o3r = O3R()
ext_calib =
{
    "ports": {
        "port2": {
            "processing": {
                "extrinsicHeadToUser": {
                    "rotX": -1.57,
                    "rotY": 1.57,
                    "rotZ": 0.0,
                    "transX": 0.0,
                    "transY": 0.0,
                    "transZ": 0.2
                }
            }
        }
    }
}
o3r.set(ext_calib)
```

Using the viewer of your choice, for example the ifmVisionAssistant, you can see the difference before and after the calibration.


## Ports selection

A VPU (OVP800) can connect up to 6 3D imager, ranging from `Port 0` to `Port 5`. Providing the port information to the ODS configuration tells the system which heads should be used for the ODS application itself.

:::{warning}
    The current ODS version do not support more than 3 used heads within an ODS application.
:::

```json
"ports": [
            "port2",
            "port3",
            "port6"
          ],
```
Connected heads, which are not defined within the ODS JSON can be used in parallel to the ODS application.
`port6` is the `IMU` (Inertial Measurement Unit) and is used by ODS. **`port6` *must always* be provided to an ODS application.**

:::{note} We recommend turning all the unused camera heads to "CONF" mode, to avoid them using up system resources. This is especially true for unused RGB cameras.
:::

## Visual odometry

`vo` - Visual odometry - is an algorithmic approach to provide - together with the IMU - ego motion data to the ODS algorithm. Images from one head are used together with the IMU data to continuously improve the ODS ego-motion estimation. The best performance is achieved by using a head with (the most) floor data visible in its images. The floors distance range needs to be at least between 1.00m and 1.50m.

Provide the port number (head with floor data in the images) to the `vo` attribute.

```json
"vo": {
    "voPorts": ["port2"]
}
```
