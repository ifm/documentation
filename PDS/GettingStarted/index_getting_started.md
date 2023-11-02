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
    ```{image} resources/step_1_iva_man_calibration.png
   :alt: Step 1
   :width: 800px
   :align: center
   ```
2. Select the port to calibrate
3. Select the orientation of camera mounted when looking from the front of camera.
4. Input the translation parameters i.e the translation distances from user/robot coordinate system to the camera
5. Finally, click on `Rotate like a vehicle front camera` to calibrate.

    ```{image} resources/step_2_to_5_iva_man_calibration.png
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
   1. User can set the command to be processed under the `customization/command` option.
      1. `nop` --> No Operation.
      
      2. `getPallet` --> Triggers the algorithm to detect the pallet in the camera's field of view. There are two parameters to configure the `getPallet` command.
         1. `depthHint`: Approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the pallet.By default it is set to **-1** to use an auto-detection of the distance. Please note that this works best with pallets having full-size loads and will most likely fail on empty pallets.
         2. `palletIndex`: Index of the pallet type. The ifm has developed PDS based on standardized pallets (Block/Stringer/EPAL side). 
         3. `palletOrder`: Set the order of pallets based on their `score`/`height`(height from floor)
      
      3. `getRack` --> Triggers the algorithm to detect the industrial rack considering the folowing parameters.
         1. `clearingVolume`: The bounding box parameters in the camera's FoV where the position of rack is expected.
         2. `depthHint`: Approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the rack. The default value is `1.8 m`.
         3. `horizontalDropPosition`: Selection of the horizontal drop setting. The user has to specify the upright to PDS algorithm to detect the pose of a rack. User can input
            1. `left`: To detect the left upright and output the pose of the rack's bottom left corner.
            2. `right`: To detect the right upright and output the pose of the rack's bottom right corner.
            3. `center`: Set this parameter when there is no information about upright is available. The PDS makes the decision based on detection score.
         4. `verticalDropPosition`: Selection of the vertical drop setting. The user has to specify the drop position to PDS algorithm. User can input
            1. `interior`: When the user wants to drop the items/pallets over the rack's beam
            2. `floor`: When the user wants to drop the items/pallets under the rack's beam and on the floor.
         5. `zHint`: Approximate distance from the coordinate system's center to the rack's beam.
   
      4. `getItem` --> Triggers the algorithm to detect the customized item (For example: Dolleys/Trolleys) considering the folowing parameters. This functionality is available only for specific items. Please contact the ifm support team to avail this functionality to your item.
          1. `depthHint`: Approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the pallet.By default it is set to **-1** to use an auto-detection of the distance. Please note that this works best with pallets having full-size loads and will most likely fail on empty pallets.
          2. `itemIndex`: Index of the item type.
          3. `itemOrder`: Set the order of detected items(when multiple items are detected) based on their `score`/`height`(height from floor)

      5. `volCheck` --> Triggers the algorithm to detect the number of valid pixels in a user-defined region of interest.
         1. `xMax`: Maximum bounding box dimension of VOI along X-Axis.
         2. `xMin`: Minimum bounding box dimension of VOI along X-Axis.
         3. `yMax`: Maximum bounding box dimension of VOI along Y-Axis.
         4. `yMin`: Minimum bounding box dimension of VOI along Y-Axis.
         5. `zMax`: Maximum bounding box dimension of VOI along Z-Axis.
         6. `zMin`: Minimum bounding box dimension of VOI along Z-Axis.

Please follow the following GIF to set up the PDS application via ifmVisionAssistant.

![PDS via iVA](resources/pds_app.gif)
