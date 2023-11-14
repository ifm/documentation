# Getting started with PDS

## Prerequisites

It is expected that a running O3R system (VPU and heads) is connected. Please refer to the [unboxing section](../../GettingStarted/Unboxing/hw_unboxing.md).

A typical procedure for getting started would be as follows
+ Connect M04311-VPU to heads and power supply
+ Power up the system
+ Connect to ifmVisionAssistant (iVA)
+ Verify that live images are being received

## Calibrate the camera

The standard O3R coordinate system is right-handed, with
* x-axis points in the opposite direction to the FAKRA connector
* y-axis points "up".
* z-axis points away from the camera (depth).

For PDS, this coordinate system is rotated to match the user/robot coordinate system.
* x-axis points away from the camera
* y-axis points to the left, and
* z-axis points up

A new feature is introduced in the latest ifmVisionAssistant (iVA), which allows the user to manually calibrate the cameras mounted on the vehicle with respect to the user/robot coordinate system using `Manual calibration of ports for vehicle algorithms`.

**Procedure:**

1. Click on `Manual calibration of ports for vehicle algorithms` under `Port settings` window.
    ```{image} resources/step_1_iva_man_calibration.png
   :alt: Step 1
   :width: 800px
   :align: center
   ```
2. Select the port to calibrate
3. Select the orientation of the mounted camera when looking at the front of the camera.
4. Enter the translation parameters, i.e. the translation distances from the user/robot coordinate system to the camera.
5. Finally, click `Rotate like a vehicle front camera` to calibrate.
    ```{image} resources/step_2_to_5_iva_man_calibration.png
   :alt: Step 2 to Step 5
   :width: 400px
   :align: center
   ```

## PDS with ifmVisionAssistant

Before reading this section, make sure you are familiar with the documentation page: [how to get started with the iVA](../../GettingStarted/ifmVisionAssistant/index_iVA.md).

1. Extrinsic calibration is a necessary step before creating a PDS application. Follow the instructions above to calibrate the cameras manually.
2. To create a PDS application instance, click on the `Application' window and click on **+** to create a new application.
3. Select the port to be used for PDS in the `Ports` section.
4. After creating a new PDS application, change the state of the application from `CONF` to `IDLE`.
5. Configuration:
   1. The user can set the command to be processed in the `Customization/Command` option.
      1. `nop` --> No operation.

      2. `getPallet` --> Triggers the algorithm to detect the pallet in the camera's field of view. There are two parameters to configure the `getPallet` command.
         1. DepthHint: Approximate distance (in meters along the x-axis) that the camera is expected to be away from the pallet, set to **-1** by default to use automatic distance detection. Note that this works best for pallets with full loads and will most likely fail for empty pallets.
         2. PalletIndex: Pallet type index. The ifm has developed PDS based on standardized pallets (Block/Stringer/EPAL side).
         3. PalletOrder: Sets the order of pallets based on their `score`/`height` (height from floor).

      3. `getRack` --> Triggers the industrial rack recognition algorithm, taking into account the following parameters:
               1. `clearingVolume`: The bounding box parameters in the camera's FoV where the position of the rack is expected.
               2. `depthHint`: Approximate distance (in meters along the x-axis) that the camera is expected to be away from the rack. The default value is `1.8 m`.
               3. `horizontalDropPosition`: Selection of the horizontal drop position. The user must specify the upright to PDS algorithm to detect the pose of a rack. The user can enter:
                  1. `left`: To detect the left upright and output the pose of the lower left corner of the rack.
                  2. `right`: To detect the right upright and output the pose of the lower right corner of the rack.
                  3. `center`: Set this parameter if there is no upright information available. The PDS will make the decision based on the detection score.
               4. `verticalDropPosition`: Selection of the vertical drop position. The user must specify the drop position for the PDS algorithm. The user can enter:
                  1. `inside`: When the user wants to drop the items/pallets over the beam of the rack.
                  2. `floor`: When the user wants to drop the items/pallets under the beam of the rack and on the floor.
               5. `zHint: Approximate distance from the center of the coordinate system to the beam of the rack.

      4. `getItem` --> Triggers the algorithm to find the customized item (for example: Dolly/Trolley) using the following parameters.
         This functionality is only available for certain items. Please contact ifm support to add this functionality to your item.
               1. `depthHint`: Approximate distance (in meters along the x-axis) that the camera is expected to be away from the pallet. By default it is set to **-1** to use an automatic detection of the distance. Note that this works best for pallets with full loads and will most likely fail for empty pallets.
               2. `itemIndex`: The index of the item type.
               3. `itemOrder`: Set the order of detected items (if multiple items are detected) based on their `score`/`height` (height from ground).

      5. `volCheck` --> Triggers the algorithm to detect the number of valid pixels in a user-defined region of interest.
         1. `xMax`: Maximum bounding box dimension of VOI along X-Axis.
         2. `xMin`: Minimum bounding box dimension of VOI along X-Axis.
         3. `yMax`: Maximum bounding box dimension of VOI along Y-Axis.
         4. `yMin`: Minimum bounding box dimension of VOI along Y-Axis.
         5. `zMax`: Maximum bounding box dimension of VOI along Z-Axis.
         6. `zMin`: Minimum bounding box dimension of VOI along Z-Axis.

Please follow the following GIF to set up the PDS application via ifmVisionAssistant.

![PDS via iVA](resources/pds_app.gif)
