
# `getItem`
The `getItem` function of PDS is designed to detect the pose of a given item. To do this, PDS needs a template of the item to be detected. A template can be understood as a reference model of the object, consisting of point cloud data from one side of the object, representing the shape of the object as seen from different angles. This template serves as a basis for comparison during the pose detection process.
Please note that these templates typically allow for an angular deviation of up to 10° - 15° from the normal vector.

To detect a custom item, please contact your local ifm support or support.robotics@ifm.com for detailed instructions.

## Input

### `depthHint`
The depth hint is an approximate distance (distance in meters along the X-axis) that the camera is expected to be away from the item. The default value is -1 which can be passed to use an auto-detection of the distance.

### `itemIndex`
The ifm development team developed and tested this functionality on the following trolley types:

| `itemIndex` | Trolley type |
| --------- | ------------ |
| 0         | `TA LSB`     |

<!-- | 1         | `TA SS`      |
| 2         | `Dolly BR`   | -->

### `itemOrder`
When multiple items are detected then the order of the detected items can be set based on the following properties.

- `scoreDescending` (default): the item order will be based upon the detection score (highest to lowest)
- `zAscending`/`zDescending`: the item order will be based upon the height from the floor (`zAscending` - lower to upper, `zDescending` - upper to lower).

## Output

| Name             | Type          | Description                      |
| ---------------- | ------------- | -------------------------------- |
| `numDetectedItems` | `uint32`        | Number of valid items in the FOV |
| `item`             | `itemDetection` | Information of item's pose. Array of `itemDetection` Structure |

#### `itemDetection` Structure
| Name     | Type       | Description                        |
| -------- | ---------- | ---------------------------------- |
| `score`    | `float32`  | Detection score of the item [0..1] |
| `position` | `Position3D` | Cartesian coordinates of the item  |
| `angles`   | `Angles3D`   | Rotation angles of the item        |

#### `Position3D` structure
| Name | Type      | Description                      |
| ---- | --------- | -------------------------------- |
| `x`    | `float32` | Cartesian X coordinate in meters |
| `y`    | `float32` | Cartesian Y coordinate in meters |
| `z`    | `float32` | Cartesian Z coordinate in meters |

#### `Angles3D` structure

| Name | Type      | Description                       |
| ---- | --------- | --------------------------------- |
| `rotX` | `float32` | Rotation around X-axis in radians |
| `rotY` | `float32` | Rotation around Y-axis in radians |
| `rotZ` | `float32` | Rotation around Z-axis in radians |

## Example

To initialize and configure the PDS application to execute `getItem` command, please see the code example below.

:::{literalinclude} ../Python/getItem.py
:caption: getItem.py
:language: python
:::