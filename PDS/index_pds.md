# PDS (Pose Detection System)

PDS - `Pose Detection System` - provided by [ifm](https://www.ifm.com), is a software solution building on top of the O3R ecosystem to enable AGVs (Automated Guided Vehicles), fork trucks and other robots to detect the pose of objects within a 3D environment.

**PDS Features**

PDS uses the O3R 3D camera as its primary data source: at least one 3D camera stream is required.

PDS provides four different commands:
| **Command** | **Output**                                                                      |
| ----------- | ------------------------------------------------------------------------------- |
| `getPallet` | Pose of the pallet                                                              |
| `getRack`   | Pose of an industrial rack                                                      |
| `getItem`   | Pose of a custom item                                                           |
| `volCheck`  | Quantifies the number of valid pixels within a defined volume of interest (VOI) |


## Compatibility Matrix

| Firmware Version | Supported VPU Hardware | Supported Camera Hardware | ifm3d-library | ifmVisionAssistant |
| ---------------- | ---------------------- | ------------------------- | ------------- | ------------------ |
| 1.2.x            | `M04311`               | O3R222                    | >=1.4.3       | >=2.7.2            |

:::{toctree}
    :maxdepth: 2
Getting started <GettingStarted/index_getting_started>
Application notes <PDS/application_notes>
:::