# Application Notes

## getPallet

The `getPallet` functionality of PDS is designed to detect the position and orientation of pallets in the vicinity of autonomous and semi-autonomous pallet handling vehicles. Typically, such a system has a priori knowledge from warehouse management, such as the approximate distance to the pallet and the type of pallet.

`getPallet` supports the picking operation by determining the exact location and orientation of the pallet.

#### Usage guidelines
The typical use cases for `getPallet` are pallets with two pockets, either with broad blocks or thin stringers as vertical support structures.
![getPallet Usage](resources/getPallet_usage.png)

<!-- **Composed pallets** TODO -->

#### Input Parameters

**Depth Hint**
The Depth Hint is the approximate distance (in meters along the X-axis) between the camera and the pallet. Depending on additional extrinsic calibration values, the distance along the X-axis can be increased or decreased with respect to the Robot Coordinate System (RCS) Zero or a negative value can be passed to use automatic distance detection. Note that this works best with full pallets and will most likely fail with empty pallets.
.
**palletIndex**

Input the pallet index based on the pallet type.

| Pallet Index | Pallet type |
| ------------ | ----------- |
| 0(default)   | `Block`     |
| 1            | `Stringer`  |
| 2            | `EPAL side` |

Other variants of pallets, having three or more pockets for example, will also work with PDS, but require adjustments of the PDS settings. Please contact the ifm support team, if you need to detect further pallet types.

**palletOrder**
If the multiple pallets were detected in the field of view then you can set the order of pallets based on three properties.
- `scoreDescending`(default): The pallet order will be based upon the score (highest to lowest)
- `zAscending`/`zDescending`: The pallet order will be based upon the height from floor, i.e. along the calibrated Z-axis (`zAscending` - lower to upper, `zDescending` - upper to lower).

#### Output

1. **numDetectedPallets** : Returns the number of valid pallets detected by the PDS in camera's FoV. (Data type: `uint32`)
2. **pallet**             : Information about pallet's pose. The structure of pallet is given below.

| Name               | Type            | Description                        |
| ------------------ | --------------- | ---------------------------------- |
| numDetectedPallets | `uint32`          | Number of valid pallets in the FoV |
| pallet             | `PalletDetection` | Array of PalletDetection Structure |

**`PalletDetection` Structure**
| Name   | Type               | Description                                                       |
| ------ | ------------------ | ----------------------------------------------------------------- |
| score  | `float32`          | Detection score of the pallet [0..1]                              |
| center | `DetectedPalletItem` | Center Position and size information of the pallet's center block |
| left   | `DetectedPalletItem` | Center Position and size information of the pallet's right pocket |
| right  | `DetectedPalletItem` | Center Position and size information of the pallet's left pocket  |
| angles | `Angles3D`           | Rotation angles of the pallet                                     |

**`DetectedPalletItem` structure**
| Name     | Type       | Description                       |
| -------- | ---------- | --------------------------------- |
| position | `Position3D` | Cartesian coordinates of the item |
| width    | `float32`  | Width of the item in meters       |
| height   | `float32`  | Height of the item in meters      |

**`Position3D` structure**
| Name | Type      | Description                      |
| ---- | --------- | -------------------------------- |
| x    | `float32` | Cartesian x coordinate in meters |
| y    | `float32` | Cartesian y coordinate in meters |
| z    | `float32` | Cartesian z coordinate in meters |

**`Angles3D` structure**

| Name | Type      | Description                       |
| ---- | --------- | --------------------------------- |
| rotX | `float32` | Rotation around x-axis in radians |
| rotY | `float32` | Rotation around y-axis in radians |
| rotZ | `float32` | Rotation around z-axis in radians |


```json
{
    "score": Detection score of the pallet [0 ... 1]
    "center": {                                         # Center Position and size information of the pallet's center block
        "position": {
            "x": Cartesian x coordinate in meters,
            "y": Cartesian y coordinate in meters,
            "z": Cartesian z coordinate in meters
            },
        "width": Width of the item in meters,
        "height": Height of the item in meters
        },
    "left": {                                         # Center position and size information of the pallet's left pocket
        "position": {
            "x": Cartesian x coordinate in meters,
            "y": Cartesian y coordinate in meters,
            "z": Cartesian z coordinate in meters
            },
        "width": Width of the item in meters,
        "height": Height of the item in meters
        },
    "right": {                                       # Center position and size information of the pallet's right pocket
        "position": {
            "x": Cartesian x coordinate in meters,
            "y": Cartesian y coordinate in meters,
            "z": Cartesian z coordinate in meters
            },
        "width": Width of the item in meters,
        "height": Height of the item in meters
        },
    "angles": {                                     # Rotation angles of the pallet
        "rotX": rotation around x-axis in radians,
        "rotY": rotation around y-axis in radians,
        "rotZ": rotation around z-axis in radians
    }
}
```

To initialize and configuring the PDS application to execute `getPallet` command, please see the code example below.

:::{literalinclude} Examples/getPallet.py
:caption: getPallet.py
:language: python
:::

## volCheck

The `volCheck`(short for Volume Check) functionality of PDS offers an easy-to-use possibility to test whether a 3D box volume (Volume Of Interest - VOI) is free of obstacles, i.e. object. An obstacle is defined by an adjustable pixel-count threshold. This command is useful to check whether the block stack or floor drop for obstacles is occupied or not before placing the load.

#### Input
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
#### Output

**numPixels** : Number of valid pixels inside the given volume of interest. (Data type: `uint32`)

:::{literalinclude} Examples/volCheck.py
:caption: volCheck.py
:language: python
:::

## getItem
The `getItem` function of PDS is designed to detect the pose of a given item. To do this, PDS needs a template of the item to be detected. A template can be understood as a reference model of the object, consisting of point cloud data from one side of the object, representing the shape of the object as seen from different angles. This template serves as a basis for comparison during the pose detection process.
Please note that these templates typically allow for an angular deviation of up to 10° - 15° from the normal vector.

To detect a custom item, please contact your local ifm support or support.robotics@ifm.com for detailed instructions for this use case.

#### Input Parameters

**Depth Hint:**
The Depth Hint is an approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the item. The default value is **-1** which can be passed to use an auto-detection of the distance.

**itemIndex:**
The ifm development team developed and tested this functionality on the following trolley types corresponding to their item index.

| itemIndex | Trolley type |
| --------- | ------------ |
| 0         | `TA LSB`     |

<!-- | 1         | `TA SS`      |
| 2         | `Dolly BR`   | -->

**itemOrder:**
When multiple items are detected then the order of the detected items can be set based on the following properties.

- `scoreDescending`(default): The item order will be based upon the score (highest to lowest)
- `zAscending`/`zDescending`: The item order will be based upon the height from floor.(`zAscending` - lower to upper, `zDescending` - upper to lower)

#### Output Parameters

**numDetectedItems:**
Number of items detected in the camera's FoV.

**item:**
Information of item's pose. The output structure of an item is given below.

| Name             | Type          | Description                      |
| ---------------- | ------------- | -------------------------------- |
| numDetectedItems | `uint32`        | Number of valid items in the FoV |
| item             | `itemDetection` | Array of itemDetection Structure |

**`itemDetection` Structure**
| Name     | Type       | Description                        |
| -------- | ---------- | ---------------------------------- |
| score    | `float32`  | Detection score of the item [0..1] |
| position | `Position3D` | Cartesian coordinates of the item  |
| angles   | `Angles3D`   | Rotation angles of the item        |

**`Position3D` structure**
| Name | Type      | Description                      |
| ---- | --------- | -------------------------------- |
| x    | `float32` | Cartesian x coordinate in meters |
| y    | `float32` | Cartesian y coordinate in meters |
| z    | `float32` | Cartesian z coordinate in meters |

**`Angles3D` structure**

| Name | Type      | Description                       |
| ---- | --------- | --------------------------------- |
| rotX | `float32` | Rotation around x-axis in radians |
| rotY | `float32` | Rotation around y-axis in radians |
| rotZ | `float32` | Rotation around z-axis in radians |

To initialize and configure the PDS application to execute `getItem` command, please see the code example below.

:::{literalinclude} Examples/getItem.py
:caption: getItem.py
:language: python
:::