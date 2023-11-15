
# `volCheck`

The `volCheck`(short for Volume Check) functionality of PDS offers an easy-to-use possibility to test whether a 3D box volume (Volume Of Interest - VOI) is free of obstacles, i.e. object. An obstacle is defined by an adjustable pixel-count threshold. This command is useful to check whether the block stack or floor drop for obstacles is occupied or not before placing the load.

## Input
**Bounding box parameters for Volume of Interest(VoI)**

The default bounding box parameters for `volCheck`

```json
{
    "xMax": 2.5, Bounding box dimension of VOI along X-axis - Maximum
    "xMin": 1.0, Bounding box dimension of VOI along X-axis - Minimum
    "yMax": 0.3, Bounding box dimension of VOI along Y-axis - Maximum
    "yMin": -0.3,Bounding box dimension of VOI along Y-axis - Minimum
    "zMax": 0.4, Bounding box dimension of VOI along Z-axis - Maximum
    "zMin": 0.1  Bounding box dimension of VOI along Z-axis - Minimum

}
```
## Output

**numPixels** : Number of valid pixels inside the given volume of interest. (Data type: `uint32`)

## Example

:::{literalinclude} ../Python/volCheck.py
:caption: volCheck.py
:language: python
:::
