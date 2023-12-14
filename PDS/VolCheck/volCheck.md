
# `volCheck`

The `volCheck`(short for volume check) functionality of PDS offers an easy-to-use possibility to test whether a 3D volume (Volume Of Interest - VOI) is free of obstacles. An obstacle is defined by an adjustable pixel-count threshold. This command is useful to check whether the location is occupied or not before placing the load.

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
| `numPixels` | `uint32` | Number of valid pixels inside the given volume of interest. |

## Example

:::{literalinclude} ../Python/volCheck.py
:caption: volCheck.py
:language: python
:::
