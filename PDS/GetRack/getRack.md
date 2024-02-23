# `getRack`

The `getRack` functionality of PDS is designed to help an AGV to safely place a pallet or load into a standard racking system. The `getRack` function has two phases:
   1. Detection of the position of the rack, 
   2. Detection of any obstacle present within a specified volume.

![`getRack`](resources/getRack_result_array.png)

In the above picture, the vertical blue line is the estimated upright structure and the horizontal green line is the estimated horizontal beam (the shelf on which the pallet will be placed).

## Coordinate system

The origin of the rack coordinate system is the intersection of the detected upright and the beam, on the plane formed by the beam and the upright's front faces.
If the left upright is segmented then the Y-axis of the rack coordinate reference frame points to the right and if the right upright is segmented then the Y-axis will point towards the left.

## Input

### `depthHint` 
The depth hint is an approximate distance in meters along the X-axis from the origin of the reference coordinate system (typically the fork tines coordinate system) to the rack. The default value is 1.8 m.
To optimize the detection process, we recommend the user configured the depth hint to the actual distance.

### `horizontalDropPosition`
The drop operation of the pallet is based on the `horizontalDropPosition` parameter. There are three configurations available for this parameter:
- `left`: if the drop operation has to take place on the left side of the shelf. The left upright of the rack is considered as a reference.
- `right`: if the drop operation has to take place on the right side of the shelf. The right upright of the rack is considered as a reference.
- `center`: if the user wishes to drop the pallet in the center. In this case, the algorithm can use a detected up-beam on either side or another pallet on the same rack as a reference. If no reference is found on either side, the leftmost part of the horizontal beam will be used.

### `verticalDropPosition`
This parameter informs the PDS about the drop location of the pallet. Depending on the drop vertical drop position, this parameter can be configured as:
- `interior` (default): if the pallet has to be dropped on the interior shelf, which is one or more levels off the ground.
- `floor`: if the drop operation is to take place directly on the floor or on a bottom shelf that is very near to the floor.

### `zHint`
The Z-hint is the approximate expected height (distance in meters along the Z axis) of the front beam with respect to the origin of the coordinate system. `getRack` uses this value to optimize the search volume (and thus performance). The Z-hint should be within +/- 0.4 m of the true height of the front beam.

### `clearingVolume` 
Volume to sweep for obstacles with respect to the established origin of the racking system. These values will typically be obtained from warehouse management and will correspond to the approximate volume of the load to be placed.

## Output
| Name      | Type         | Description                                                                                    |
| --------- | ------------ | ---------------------------------------------------------------------------------------------- |
| `score`     | `float32`    | Detection score of the rack [0..1]                                                             |
| `position`  | `Position3D` | Position of the rack coordinate system origin                                                  |
| `angles`    | `Angles3D`   | Rotation of the rack coordinates system                                                        |
| `side`      | `char[25]`   | Type of the rack coordinate system. Either "right" for right-handed or "left" for left-handed. |
| `numPixels` | `uint32_t`   | Number of pixels inside the volume of interest                                           |
| `flags`     | `uint32_t`   | Bitmask with debugging information for `getRack`                                                 |


### `Position3D` structure
| Name | Type      | Description                      |
| ---- | --------- | -------------------------------- |
| `x`    | `float32` | Cartesian X coordinate in meters |
| `y`    | `float32` | Cartesian Y coordinate in meters |
| `z`    | `float32` | Cartesian Z coordinate in meters |

### `Angles3D` structure

| Name | Type      | Description                       |
| ---- | --------- | --------------------------------- |
| `rotX` | `float32` | Rotation around X-axis in radians |
| `rotY` | `float32` | Rotation around Y-axis in radians |
| `rotZ` | `float32` | Rotation around Z-axis in radians |

### Flags

| Bit No. | Name                | Description                                                                                                                                  |
| ------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 0       | `NO_BEAM`           | The horizontal beam of the rack grid location could not be segmented                                                                         |
| 1       | `MULTIPLE_BEAMS`    | Multiple horizontal beam candidates were segmented, the most plausible was selected                                                          |
| 2       | `BEAM_COVERAGE`     | The threshold of pixel coverage over the surface area of the beam was not met                                                                  |
| 3       | `NO_UPRIGHT`        | A vertical upright was not detected, the rack frame was established based on the segmented beam, sweeping volume, and (optionally) the floor |
| 4       | `MULTIPLE_UPRIGHTS` | Multiple upright candidates (on the anchor side of interest) were segmented, the most plausible was selected                                 |
| 5       | `UPRIGHT_COVERAGE`  | The threshold of pixel coverage over the surface area of the upright was not met                                                               |
| 6       | `NO_JOIN`           | The beam and the upright used to establish the rack frame do not intersect in the point cloud                                                |
| 7       | `BAD_TRANSFORM`     | The origin of the computed rack frame is outside of an expected tolerance (indicative of a beam-only localization anchoring to an obstacle)  |
| 8       | `SHELF_OBSTACLE`    | An obstacle was detected within the shelf sweeping volume with respect to the established rack frame                                         |

The resultant flag value is a decimal value and has to be converted to binary value to know which flags were set to 1. If the value of the flag is set to 384 then the resultant binary value is `11000000`, that is, bit numbers 7 and 8 were set to 1 (`BAD_TRANSFORM` and `SHELF_OBSTACLE`).

In the below section, the possible reasons why the flags are set are discussed in detail.

#### `NO_BEAM`

The horizontal beam of the rack grid location could not be segmented (this is a critical error). Possible reasons are:
   - Incorrect `depthHint`: the algorithm looks for the beams around the given depth hint. The tolerance for depth hint is 0.23 m,
   - Incorrect Z-hint: the algorithm looks for beams around the provided Z-hint. The tolerance is 0.4 m,
   - No beam candidate meets the minimum length requirement: the algorithm looks for beams with a minimum length of 1.0 m,
   - No beam candidate meets min or max height requirement: the algorithm looks for beams with a minimum or maximum height of respectively 6 and 15 cm.

#### `MULTIPLE_BEAMS`

Multiple horizontal beam candidates were segmented, and the one with the largest extent in the Y-direction was selected. Possible reasons are:
   - Presence of a loaded pallet or other obstacle above or below the beam,
   - Presence of a true second beam in the scene,
   - More than one beam candidate meets the minimum length and minimum or maximum height requirements.

#### `BEAM_COVERAGE`

A threshold of pixel coverage over the surface area of the beam was not met. Possible reasons are:
   - The segmented beam has lots of non-planar points,
   - The segmented beam does not meet the minimum coverage requirement.

#### `NO_UPRIGHT`

A vertical upright was not detected, and the rack frame was established based on the segmented beam, sweeping volume, and (optionally) the floor. Possible reasons are:
   - Incorrect `horizontalDropPosition`: the algorithm looks to either the right side or left side, not to both sides except `horizontalDropPosition = center`,
   - No upright close to the beam,
   - No upright candidate meets the minimum length requirement: the algorithm looks for uprights with a minimum length of 0.6 m,
   - No upright candidate meets the minimum or maximum width requirement: the algorithm looks for uprights with a minimum or maximum width of respectively  3 or 12 cm.

#### `MULTIPLE_UPRIGHTS`

Multiple upright candidates (on the anchor side of interest) were segmented. The leftmost or the rightmost was selected, depending on the `horizontalDropPosition`. Possible reasons are:
   - Loaded pallet or other obstacle above or below the beam,
   - True second upright in the scene,
   - More than one upright candidate meets the minimum length and minimum or maximum width requirements.

#### `UPRIGHT_COVERAGE`

A threshold of pixel coverage over the surface area of the upright was not met. Possible reasons are:
   - The segmented upright has lots of non-planar points,
   - The segmented upright does not meet the minimum coverage requirement (after 3D plane fit).
-
:::{note}
   If `NO_UPRIGHT` flag is set, then `UPRIGHT_COVERAGE` is also set. 
:::

#### `NO_JOIN`

The beam and the upright used to establish the rack frame do not intersect in the point cloud. Possible reasons are:
   - The segmented beam and segmented upright do not intersect.

:::{note} 
   If `NO_UPRIGHT` flag is set, then `NO_JOIN` is also set.
:::

#### `BAD_TRANSFORM`

The origin of the computed rack frame is outside of an expected tolerance (indicative of a beam-only localization anchoring to an obstacle). Possible reasons are:
   - Position of selected upright deviates from expected position (only Y-coordinate is considered): the algorithm expects the upright to be within tolerance on either the left side or right side.

#### `SHELF_OBSTACLE`

An obstacle was detected within the shelf sweeping volume with respect to the established rack frame. Possible reasons are:
   - The obstacle was detected within the shelf clearing volume: the algorithm checks the specified shelf clearing volume (defined with respect to the rack origin) for obstacles.