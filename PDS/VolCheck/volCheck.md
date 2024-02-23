
# `volCheck`

The `volCheck`(short for volume check) functionality of PDS offers an easy-to-use possibility to test whether a 3D volume (Volume Of Interest - VOI) is free of obstacles. The number of pixels present in the defined VOI is provided, and the user can decide of their own threshold as to how many pixels are considered an obstacle. This command is useful to check whether the location is occupied or not before placing the load.

## Input

The default bounding box parameters for `volCheck`

| Name | Description |
| ---- | ----------- |
| `xMax` | Bounding box dimension of VOI along X-axis - Maximum |
| `xMin` | Bounding box dimension of VOI along X-axis - Minimum | 
| `yMax` | Bounding box dimension of VOI along Y-axis - Maximum |
| `yMin` | Bounding box dimension of VOI along Y-axis - Minimum |
| `zMax` | Bounding box dimension of VOI along Z-axis - Maximum |
| `zMin` | Bounding box dimension of VOI along Z-axis - Minimum |


## Output

| Name | Type | Description |
| ---- | ---- | ----------- |
| `numPixels` | `uint32` | Number of valid pixels inside the given volume of interest. |

## Example

:::{literalinclude} ../Python/volCheck.py
:caption: volCheck.py
:language: python
:::
