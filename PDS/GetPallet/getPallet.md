
# `getPallet`

The `getPallet` functionality of PDS is designed to detect the position and orientation of pallets in the vicinity of autonomous and semi-autonomous pallet handling vehicles. Typically, such a system has a priori knowledge from warehouse management, such as the approximate distance to the pallet and the type of pallet.

`getPallet` supports the picking operation by determining the exact location and orientation of the pallet.

## Usage guidelines
The typical use cases for `getPallet` are pallets with two pockets, either with broad blocks or thin stringers as vertical support structures.
![getPallet Usage](resources/getPallet_usage.png)

<!-- **Composed pallets** TODO -->

## Input

### `depthHint`
The Depth Hint is the approximate distance (in meters along the X-axis) between the camera and the pallet. Depending on additional extrinsic calibration values, the distance along the X-axis can be increased or decreased with respect to the Robot Coordinate System (RCS) Zero or a negative value can be passed to use automatic distance detection. Note that this works best with full pallets and will most likely fail with empty pallets.
.

### `palletIndex`

Input the pallet index based on the pallet type.

| Pallet Index | Pallet type |
| ------------ | ----------- |
| 0(default)   | `Block`     |
| 1            | `Stringer`  |
| 2            | `EPAL side` |

Other variants of pallets, having three or more pockets for example, will also work with PDS, but require adjustments of the PDS settings. Please contact the ifm support team, if you need to detect further pallet types.

### `palletOrder`
If the multiple pallets were detected in the field of view then you can set the order of pallets based on three properties.
- `scoreDescending`(default): The pallet order will be based upon the score (highest to lowest)
- `zAscending`/`zDescending`: The pallet order will be based upon the height from floor, i.e. along the calibrated Z-axis (`zAscending` - lower to upper, `zDescending` - upper to lower).

## Output

1. **numDetectedPallets** : Returns the number of valid pallets detected by the PDS in camera's FoV. (Data type: `uint32`)
2. **pallet**             : Information about pallet's pose. The structure of pallet is given below.

| Name               | Type            | Description                        |
| ------------------ | --------------- | ---------------------------------- |
| numDetectedPallets | `uint32`          | Number of valid pallets in the FoV |
| pallet             | `PalletDetection` | Array of PalletDetection Structure |

### `PalletDetection` Structure
| Name   | Type               | Description                                                       |
| ------ | ------------------ | ----------------------------------------------------------------- |
| score  | `float32`          | Detection score of the pallet [0..1]                              |
| center | `DetectedPalletItem` | Center Position and size information of the pallet's center block |
| left   | `DetectedPalletItem` | Center Position and size information of the pallet's right pocket |
| right  | `DetectedPalletItem` | Center Position and size information of the pallet's left pocket  |
| angles | `Angles3D`           | Rotation angles of the pallet                                     |

#### `DetectedPalletItem` structure
| Name     | Type       | Description                       |
| -------- | ---------- | --------------------------------- |
| position | `Position3D` | Cartesian coordinates of the item |
| width    | `float32`  | Width of the item in meters       |
| height   | `float32`  | Height of the item in meters      |

##### `Position3D` structure
| Name | Type      | Description                      |
| ---- | --------- | -------------------------------- |
| x    | `float32` | Cartesian x coordinate in meters |
| y    | `float32` | Cartesian y coordinate in meters |
| z    | `float32` | Cartesian z coordinate in meters |

#### `Angles3D` structure

| Name | Type      | Description                       |
| ---- | --------- | --------------------------------- |
| rotX | `float32` | Rotation around x-axis in radians |
| rotY | `float32` | Rotation around y-axis in radians |
| rotZ | `float32` | Rotation around z-axis in radians |

## Example

To initialize and configuring the PDS application to execute `getPallet` command, please see the code example below.

:::{literalinclude} ../Python/getPallet.py
:caption: getPallet.py
:language: python
:::