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
   1. User can set the command to be processed under `customization/command` option.
      1. `nop` --> No Operation.
      2. `getPallet` --> Triggers the algorithm to detect the pallet in the camera's field of view. There are two parameters to configure the `getPallet` command.
         1. `depthHint`: Approximate distance (distance in meters along the x-axis) that the camera is expected to be away from the pallet.By default it is set to **-1** to use an auto-detection of the distance. Please note that this works best with pallets having full-size load and will most likely fail on empty pallets.
         2. `palletIndex`: Index of the pallet type. The ifm has developed PDS based on standardized pallets as below. 
         <!-- 3. TODO -->
      3. `getRack` --> Triggers the algorithm to detect the industrial rack at given depthHint and

