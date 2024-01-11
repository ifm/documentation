
# `getPallet`

The `getPallet` functionality of PDS is designed to detect the position and orientation of pallets in the vicinity of autonomous and semi-autonomous pallet handling vehicles. Typically, such a system has a priori knowledge from warehouse management, such as the approximate distance to the pallet and the type of pallet.

`getPallet` supports the picking operation by determining the exact location and orientation of the pallet.

## Usage guidelines
The typical use cases for `getPallet` are pallets with two pockets, either with broad blocks or thin stringers as vertical support structures.
![`getPallet` Usage](resources/getPallet_usage.png)

PDS is able to detect pallets with the following characteristics:
- For a block-type pallet:
    - The pockets should be between 0.24 and 0.44 m,
    - The blocks should be between 0.05 and 0.4 m.
- For a stringer-type pallet:
    - The pockets should be between 0.4 and 0.48 m,
    - The stringers should be between 0.02 and 0.08 m.

Two pocket pallets with different dimensions than the ones stated above will require specific configuration of the algorithm. Reach out to your ifm representative or to the support team for more details.

## Input

### `depthHint`
The depth hint is the approximate distance (in meters along the X-axis) between the camera and the pallet. Providing an accurate depth hint allows the algorithm to target a specific area of the scene for the pallet detection and speeds up processing times.
Zero or a negative value can be passed to use automatic distance detection. Note that automatic detection works best with fully loaded pallets and will most likely fail with empty pallets.

### `palletIndex`

Input the pallet index based on the pallet type.

| Pallet Index | Pallet type |
| ------------ | ----------- |
| 0 (default)  | `Block`     |
| 1            | `Stringer`  |
| 2            | `EPAL side` |

Other variants of pallets, having three or more pockets for example, require adjustments of the PDS settings. Reach out to your ifm representative or to the support team for more details.

### `palletOrder`
If multiple pallets were detected in the field of view, you can set the order of pallets based on three properties:
- `scoreDescending` (default): the pallet order will be based upon the detection score (highest to lowest), which corresponds to how well the pallet matches the expected pallet shape,
- `zAscending`/`zDescending`: the pallet order will be based upon the height from the floor, that is, along the calibrated Z-axis (`zAscending` - lower to upper, `zDescending` - upper to lower).

## Output

| Name               | Type            | Description                        |
| ------------------ | --------------- | ---------------------------------- |
| `numDetectedPallets` | `uint32`          | Number of valid pallets in the FOV |
| `pallet`             | `PalletDetection` | Information about the pallet's pose. The structure of the `PalletDetection` type is given below. |

### `PalletDetection` structure
| Name   | Type               | Description                                                       |
| ------ | ------------------ | ----------------------------------------------------------------- |
| `score`  | `float32`          | Detection score of the pallet [0..1]                              |
| `center` | `DetectedPalletItem` | Position and size of the pallet's center block |
| `left`   | `DetectedPalletItem` | Position and size of the pallet's right pocket |
| `right`  | `DetectedPalletItem` | Position and size of the pallet's left pocket  |
| `angles` | `Angles3D`           | Rotation angles of the pallet                  |

#### `DetectedPalletItem` structure
| Name     | Type       | Description                       |
| -------- | ---------- | --------------------------------- |
| `position` | `Position3D` | Cartesian coordinates of the item |
| `width`    | `float32`  | Width of the item in meters       |
| `height`   | `float32`  | Height of the item in meters      |

##### `Position3D` structure
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

To initialize and configuring the PDS application to execute `getPallet` command, please see the code example below.

:::{literalinclude} ../Python/getPallet.py
:caption: getPallet.py
:language: python
:::