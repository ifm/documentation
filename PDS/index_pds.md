# PDS (Pose Detection System)


PDS - `Pose Detection System` - provided by [ifm](https://www.ifm.com), is a software solution building on top of the O3R ecosystem to enable AGVs (Automated Guided Vehicles), fork trucks and other robots to detect the pose of objects within a 3D environment. This solution has profound implications for a multitude of industries, particularly in the fields of logistics, industrial automation.

## PDS Features

PDS uses the O3R camera as its primary data source: at least one 3D camera stream is required.

**Command Flexibility**
PDS can able to process four different type of commands which are pivotal in logistics, warehouse management and facilitates the optimal material handling.

| **Command** | **Output**                                                                      |
| ----------- | ------------------------------------------------------------------------------- |
| getPallet   | Pose of the pallet                                                              |
| getRack     | Pose of an industrial rack                                                      |
| getItem     | Pose of an item                                                                 |
| volCheck    | Quantifies the number of valid pixels within a defined volume of interest (VOI) |