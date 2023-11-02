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

# Getting started with PDS

## Prerequisites

It is expected that there is a running system. Please refer to the [unboxing section](../../GettingStarted/Unboxing/hw_unboxing.md).

A typical procedure would be:
+ connect M04311-VPU with heads and power supply
+ boot-up the system
+ connect with iVA
+ verify that live images are received

## Compatibility Matrix

| Firmware Version | Supported VPU Hardware | Supported Camera Hardware | ifm3d-library | ifmVisionAssistant |
| ---------------- | ---------------------- | ------------------------- | ------------- | ------------------ |
| 1.2.x            | `M04311`               | O3R222                    | >=1.4.3       | >=2.7.2            |

## Coordinate Systems and Extrinsic Calibration

The standard O3Rxx coordinate system is right handed, with
* x-axis pointing pointing in the opposite direction from the FAKRA-connector
* y-axis is pointing “up”
* z-axis pointing away from the camera (depth).

For PDS, this coordinate system is rotated, so that it matches the User/Robotic Coordinate System
* x-axis points away from the camera
* y-axis points to the left, and
* z-axis points up

A new feature is introduced in latest ifmVisionassistant (iVA) where the user can calibrate the cameras mounted on the vehicle with respect to user/robot coordinate system manually using `Manual calibration of ports for vehicle algorithms`.

**Procedure:**

1. Click on `Manual calibration of ports for vehicle algorithms` under `Port settings` window.
    ```{image} GettingStarted/resources/step_1_iva_man_calibration.png
   :alt: Step 1
   :width: 800px
   :align: center
   ```
2. Select the port to calibrate
3. Select the orientation of camera mounted when looking from the front of camera.
4. Input the translation parameters i.e the translation distances from user/robot coordinate system to the camera
5. Finally, click on `Rotate like a vehicle front camera` to calibrate.

    ```{image} GettingStarted/resources/step_2_to_5_iva_man_calibration.png
   :alt: Step 2 to Step 5
   :width: 400px
   :align: center
   ```

## PDS with ifmVisionassistant

Before reading this section, make sure to read [how to get started with the iVA](../../GettingStarted/ifmVisionAssistant/index_iVA.md).

1. Extrinsic calibration is pre-requisite stepp before creating a PDS application. Follow the above guide to calibrate the cameras manually.
2. To create a PDS application instance, click on `Application` window and click on **+** to create a new application.
3. After creating a new PDS application, change the state of application from `CONF` to `IDLE`.
4. To choose the port to be used for PDS, user has to pause the application and select the port under `ports` section.
5. `Configuation`:
   1. User can set the command to be processed under `customization/command` option.
      1. `nop` --> No Operation.
      
      2. `getPallet` --> Triggers the algorithm to detect the pallet in the camera's field of view. There are two parameters to configure the `getPallet` command.
         1. `depthHint`: Approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the pallet.By default it is set to **-1** to use an auto-detection of the distance. Please note that this works best with pallets having full-size load and will most likely fail on empty pallets.
         2. `palletIndex`: Index of the pallet type. The ifm has developed PDS based on standardized pallets (Block/Stringer/EPAL side). 
         3. `palletOrder`: Set the order of pallets based on their `score`/`height`(height from floor)
      
      3. `getRack` --> Triggers the algorithm to detect the industrial rack considering the folowing parameters.
         1. `clearingVolume` : The bounding box parameters in the camera's FoV where the position of rack is expected.
         2. `depthHint`: Approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the rack. The default value is `1.8 m`.
         3. `horizontalDropPosition`:Selection of the horizontal drop setting. The user has to specify the upright to PDS algorithm to detect the pose of a rack. User can input
            1. `left`: To detect the left upright and output the pose of the rack's bottom left corner.
            2. `right`: To detect the right upright and output the pose of the rack's bottom right corner.
            3. `center`: Set this parameter when there is no information about upright is available. The PDS makes the decision based on detection score.
         4. `verticalDropPosition`: Selection of the vertical drop setting. The user has to specify the drop position to PDS algorithm. User can input
            1. `interior`: When user wants to drop the items/pallets over the rack's beam
            2. `floor`: When user wants to drop the items/pallets under the rack's beam and on floor.
         5. `zHint`: Approximate distance from coordinate system's center to the rack's beam.
   
      4. `getItem` --> Triggers the algorithm to detect the customized item (For example: Dolleys/Trolleys) considering the folowing parameters. This functionality is available only for specific items. Please contact the ifm support team to avail this functionality to your item.
          1. `depthHint`: Approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the pallet.By default it is set to **-1** to use an auto-detection of the distance. Please note that this works best with pallets having full-size load and will most likely fail on empty pallets.
          2. `itemIndex`: Index of the item type.
          3. `itemOrder`: Set the order of detected items(when multiple items are detected) based on their `score`/`height`(height from floor)

      5. `volCheck` --> Triggers the algorithm to detect the number of valid pixels in user-defined region of interest.
         1. `xMax`:Maximum bounding box dimension of VOI along X-Axis 
         2. `xMin`:Minimum bounding box dimension of VOI along X-Axis 
         3. `yMax`:Maximum bounding box dimension of VOI along Y-Axis 
         4. `yMin`:Minimum bounding box dimension of VOI along Y-Axis 
         5. `zMax`:Maximum bounding box dimension of VOI along Z-Axis 
         6. `zMin`:Minimum bounding box dimension of VOI along Z-Axis 

Please follow the following GIF to setup the PDS application via ifmVisionAssistant.

![PDS via iVA](GettingStarted/resources/pds_app.gif)

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Application Notes

## getPallet

The `getPallet` functionality of PDS is designed to detect the position and orientation of pallets in front of autonomous and semi-autonomous pallet handling vehicles. Usually, such a system has a priori knowledge from the warehouse management like the approximate distance to the pallet and the pallet type.

`getPallet` supports the pick-operation by detecting the precise location of the pallet. In case of unexpected situations like occluded pockets or missing pallet blocks, the pick is considered to be unsafe and the detection will be aborted.

#### Usage guidelines
The typical use cases for `getPallet` are pallets with two pockets, either with broad blocks or thin stringers as vertical support structures.
![getPallet Usage](resources/getPallet_usage.png)

<!-- **Composed pallets** TODO -->

#### Input Parameters

**Depth Hint**
The Depth Hint is the approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the pallet. Zero or a negative value can be passed to use an auto-detection of the distance. Please note that this works best with pallets having full-size load and will most likely fail on empty pallets.

**palletIndex**

Input the pallet index based on the pallet type.

| Pallet Index | Pallet type |
| ------------ | ----------- |
| 0(default)   | `Block`     |
| 1            | `Stringer`  |
| 2            | `EPAL side` |

Other variants of pallets, having three or more pockets for example, might also work with PDS, but will require adjustments of the PDS settings. Please contact the ifm support team, if you need to detect further pallet types.

**palletOrder**
If the multiple pallets were detected in the field of view then you can set the order of pallets based on three properties.
- `scoreDescending`(default): The pallet order will be based upon the score (highest to lowest)
- `zAscending`/`zDescending`: The pallet order will be based upon the height from floor.(`zAscending` - lower to upper, `zDescending` - upper to lower)

#### Output

1. **numDetectedPallets** : Returns the number of valid pallets detected by the PDS in camera's FoV. (Data type: `uint32`)
2. **pallet**             : Information about pallet's pose. The structure of pallet is given below.

| Name               | Type            | Description                        |
| ------------------ | --------------- | ---------------------------------- |
| numDetectedPallets | uint32          | Number of valid pallets in the FoV |
| pallet             | PalletDetection | Array of PalletDetection Structure |

**PalletDetection Structure**
| Name   | Type               | Description                                                       |
| ------ | ------------------ | ----------------------------------------------------------------- |
| score  | `float32`          | Detection score of the pallet [0..1]                              |
| center | DetectedPalletItem | Center Position and size information of the pallet's center block |
| left   | DetectedPalletItem | Center Position and size information of the pallet's right pocket |
| right  | DetectedPalletItem | Center Position and size information of the pallet's left pocket  |
| angles | Angles3D           | Rotation angles of the pallet                                     |

**DetectedPalletItem structure**
| Name     | Type       | Description                       |
| -------- | ---------- | --------------------------------- |
| position | Position3D | Cartesian coordinates of the item |
| width    | `float32`  | Width of the item in meters       |
| height   | `float32`  | Height of the item in meters      |

**Position3D structure**
| Name | Type      | Description                      |
| ---- | --------- | -------------------------------- |
| x    | `float32` | Cartesian x coordinate in meters |
| y    | `float32` | Cartesian y coordinate in meters |
| z    | `float32` | Cartesian z coordinate in meters |

**Angles3D structure**

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

To initialize a nd configuring the PDS application to execute `getPallet` command, please see the code example below.

```python
###########################################
###2023-present ifm electronic, gmbh
###SPDX-License-Identifier: Apache-2.0
###########################################
"""
Setup:  * O3R222   3D on port2 
            * orientation: camera horizontally (Fakra cable to the left)
        * getPallet: pallet with load in FoV @ 1.5m distance
"""
import ifm3dpy
from ifm3dpy.device import Error as ifm3dpy_error
import json
from ifm3dpy.framegrabber import FrameGrabber, buffer_id
import numpy as np
import time
import default_values

o3r = ifm3dpy.O3R()
try:
    o3r.reset("/applications/instances")
except Exception as e:
    print("Reset failed: %s" % (e))
    pass

c = dict(transX=0.0, transY=0, transZ=0.0, rotX=-1.57, rotY=1.57, rotZ=0)
print("set(/ports/port2/processing/extrinsicHeadToUser)")
o3r.set({"ports": {"port2": {"processing":{"extrinsicHeadToUser": c}}}})

print("set(/applications/instances/app0/class:pds, ports:port2)")
o3r.set({"applications": {"instances": {"app0": {"class": "pds", "ports": ["port2"]}}}})

print("set(/applications/instances/app0/state:IDLE)")
o3r.set({"applications": {"instances": {"app0": {"state": "IDLE"}}}})

time.sleep(0.5)

print("create framegrabber instance")
fg = FrameGrabber(o3r,51010)

PCIC_FORMAT = {
  "layouter": "flexible",
  "format": {
    "dataencoding": "ascii"
  },
  "elements": [
    {
      "type": "string",
      "value": "star",
      "id": "start_string"
    },
    {
      "type": "blob",
      "id": "O3R_RESULT_JSON"
    },
    {
      "type": "blob",
      "id": "O3R_RESULT_ARRAY2D"
    },
    {
      "type": "string",
      "value": "stop",
      "id": "end_string"
    }
  ]
}
fg.start([1002,1003], pcic_format=PCIC_FORMAT)
print("Init done")

GET_PALLET_PARAMETERS = {
          "depthHint": -1, 
          "palletIndex": 0, # Block Pallet/EPAL pallet
          "palletOrder": "scoreDescending"
        }

o3r.set({"applications": {"instances": {"app0": {"configuration": {"customization":{"command": "getPallet", "getPallet":GET_PALLET_PARAMETERS }}}}}})
[ok, frame] = fg.wait_for_frame().wait_for(6000)

if ok:
    if frame.has_buffer(buffer_id(1003)):
            json_chunk = frame.get_buffer(buffer_id(1002))
            json_array = np.frombuffer(json_chunk[0], dtype=np.uint8)
            json_array = json_array.tobytes()
            parsed_json_array = json.loads(json_array.decode())
            print(parsed_json_array["getPallet"]["pallet"])
```

## volCheck

The `volCheck`(short for Volume Check) functionality of PDS offers an easy to use possibility to test whether a 3D box-volume is free of obstacles. An obstacle is defined by an adjustable pixel-count threshold. This command is useful to check wether the block stack or floor drop for obstacles is occupied or not before placing the load.

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

```python
###########################################
###2023-present ifm electronic, gmbh
###SPDX-License-Identifier: Apache-2.0
###########################################
"""
Setup:  * O3R222   3D on port2 
            * orientation: camera horizontally (Fakra cable to the left)
"""
import ifm3dpy
from ifm3dpy.device import Error as ifm3dpy_error
import json
from ifm3dpy.framegrabber import FrameGrabber, buffer_id
import numpy as np
import time

o3r = ifm3dpy.O3R()
try:
    o3r.reset("/applications/instances")
except Exception as e:
    print("Reset failed: %s" % (e))
    pass

c = dict(transX=0.0, transY=0, transZ=0.0, rotX=-1.57, rotY=1.57, rotZ=0)
print("set(/ports/port2/processing/extrinsicHeadToUser)")
o3r.set({"ports": {"port2": {"processing":{"extrinsicHeadToUser": c}}}})

print("set(/applications/instances/app0/class:pds, ports:port2)")
o3r.set({"applications": {"instances": {"app0": {"class": "pds", "ports": ["port2"]}}}})

print("set(/applications/instances/app0/state:IDLE)")
o3r.set({"applications": {"instances": {"app0": {"state": "IDLE"}}}})

time.sleep(0.5)

print("create framegrabber instance")
fg = FrameGrabber(o3r,51010)

PCIC_FORMAT = {
  "layouter": "flexible",
  "format": {
    "dataencoding": "ascii"
  },
  "elements": [
    {
      "type": "string",
      "value": "star",
      "id": "start_string"
    },
    {
      "type": "blob",
      "id": "O3R_RESULT_JSON"
    },
    {
      "type": "blob",
      "id": "O3R_RESULT_ARRAY2D"
    },
    {
      "type": "string",
      "value": "stop",
      "id": "end_string"
    }
  ]
}
fg.start([1002,1003], pcic_format=PCIC_FORMAT)
print("Init done")

VOLCHECK_PARAMETERS = {
                        "xMin": 2,
                        "xMax": 3.5,
                        "yMin": -0.5,
                        "yMax": 0.5,
                        "zMin": -.8,
                        "zMax":0.4
                    }

o3r.set({"applications": {"instances": {"app0": {"configuration": {"customization":{"command": "volCheck", "volCheck":VOLCHECK_PARAMETERS }}}}}})
[ok, frame] = fg.wait_for_frame().wait_for(6000)

if ok:
    if frame.has_buffer(buffer_id(1003)):
            json_chunk = frame.get_buffer(buffer_id(1002))
            json_array = np.frombuffer(json_chunk[0], dtype=np.uint8)
            json_array = json_array.tobytes()
            parsed_json_array = json.loads(json_array.decode())
            print(parsed_json_array["volCheck"]["numPixels"])
```

## getItem

The  `getItem` functionality of PDS is developed to detect the pose of a specific item. To achieve this, the PDS requires a depth template of the item it aims to detect. A depth template is essentially a reference model of the object, consisting of 3D point cloud data that represents the item from various angles and orientations. This template serves as a basis for comparison during the pose detection process.

To detect a custom item, please contact your local ifm support or support.robotics@ifm.com for detailed instructions for this use case.

#### Input Parameters

**Depth Hint:**
The Depth Hint is an approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the item. The default value is **-1** that can be passed to use an auto-detection of the distance.

**itemIndex:**
The ifm development team had developed and tested this functionality on the following trolley types corresponding to their item index.

| itemIndex | Trolley type |
| --------- | ------------ |
| 0         | `TA LSB`     |
| 1         | `TA SS`      |
| 2         | `Dolly BR`   |

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
| numDetecteditems | uint32        | Number of valid items in the FoV |
| item             | itemDetection | Array of itemDetection Structure |

**itemDetection Structure**
| Name     | Type       | Description                        |
| -------- | ---------- | ---------------------------------- |
| score    | `float32`  | Detection score of the item [0..1] |
| position | Position3D | Cartesian coordinates of the item  |
| angles   | Angles3D   | Rotation angles of the item        |

**Position3D structure**
| Name | Type      | Description                      |
| ---- | --------- | -------------------------------- |
| x    | `float32` | Cartesian x coordinate in meters |
| y    | `float32` | Cartesian y coordinate in meters |
| z    | `float32` | Cartesian z coordinate in meters |

**Angles3D structure**

| Name | Type      | Description                       |
| ---- | --------- | --------------------------------- |
| rotX | `float32` | Rotation around x-axis in radians |
| rotY | `float32` | Rotation around y-axis in radians |
| rotZ | `float32` | Rotation around z-axis in radians |

To initialize a nd configuring the PDS application to execute `getItem` command, please see the code example below.


```python
###########################################
###2023-present ifm electronic, gmbh
###SPDX-License-Identifier: Apache-2.0
###########################################
"""
Setup:  * O3R222   3D on port2 
            * orientation: camera horizontally (Fakra cable to the left)
        * getItem: item/s in FoV @ 1.5m distance
"""
import ifm3dpy
from ifm3dpy.device import Error as ifm3dpy_error
import json
from ifm3dpy.framegrabber import FrameGrabber, buffer_id
import numpy as np
import time

o3r = ifm3dpy.O3R()
try:
    o3r.reset("/applications/instances")
except Exception as e:
    print("Reset failed: %s" % (e))
    pass

c = dict(transX=0.0, transY=0, transZ=0.0, rotX=-1.57, rotY=1.57, rotZ=0)
print("set(/ports/port2/processing/extrinsicHeadToUser)")
o3r.set({"ports": {"port2": {"processing":{"extrinsicHeadToUser": c}}}})

print("set(/applications/instances/app0/class:pds, ports:port2)")
o3r.set({"applications": {"instances": {"app0": {"class": "pds", "ports": ["port2"]}}}})

print("set(/applications/instances/app0/state:IDLE)")
o3r.set({"applications": {"instances": {"app0": {"state": "IDLE"}}}})

time.sleep(0.5)

print("create framegrabber instance")
fg = FrameGrabber(o3r,51010)

PCIC_FORMAT = {
  "layouter": "flexible",
  "format": {
    "dataencoding": "ascii"
  },
  "elements": [
    {
      "type": "string",
      "value": "star",
      "id": "start_string"
    },
    {
      "type": "blob",
      "id": "O3R_RESULT_JSON"
    },
    {
      "type": "blob",
      "id": "O3R_RESULT_ARRAY2D"
    },
    {
      "type": "string",
      "value": "stop",
      "id": "end_string"
    }
  ]
}
fg.start([1002,1003], pcic_format=PCIC_FORMAT)
print("Init done")

GET_ITEM_PARAMETERS = {
          "depthHint": -1, 
          "itemIndex": 0, # TA LSB (DHL wagon)
          "palletOrder": "scoreDescending"
        }

o3r.set({"applications": {"instances": {"app0": {"configuration": {"customization":{"command": "getItem", "getItem":GET_ITEM_PARAMETERS }}}}}})

[ok, frame] = fg.wait_for_frame().wait_for(6000)

if ok:
    if frame.has_buffer(buffer_id(1003)):
            json_chunk = frame.get_buffer(buffer_id(1002))
            json_array = np.frombuffer(json_chunk[0], dtype=np.uint8)
            json_array = json_array.tobytes()
            parsed_json_array = json.loads(json_array.decode())
            print(parsed_json_array["getItem"]["item"])
```
