# Configuration

| Parameter                                                    | Description                                                                                                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                                                       | Providing a custom name for the PDS application                                                                                                   |
| `ports`                                                      | The port that is used by the PDS application                                                                                                      |
| `state`                                                      | The current app state (default: `CONF`)                                                                                                           |
| `configuration/customization/command`                        | The command to be executed by PDS.                                                                                                                |
| `configuration/customization/command/nop`                    | No Operation State. After the command is executed by the PDS, the command parameter is set back to `nop` value                                    |
| `configuration/customization/command/getPallet`              | Trigger the `getPallet` command to output the pose of the pallet                                                                                  |
| `configuration/customization/command/getRack`                | Trigger the `getRack` command to output the pose of the rack coordinate system                                                                    |
| `configuration/customization/command/getItem`                | Trigger the `getItem` command to output the pose of the item                                                                                      |
| `configuration/customization/command/volCheck`               | Trigger the `volCheck` command to output the number of valid pixels inside the user-defined volume of interest                                    |
| `configuration/customization/getPallet/depthHint`            | An approximate distance (in meters along the X-axis) between the camera and the pallet                                                            |
| `configuration/customization/getPallet/palletIndex`          | Pallet index based on the pallet type                                                                                                             |
| `configuration/customization/getPallet/palletOrder`          | Order of the pallets detected with respect to height or score when multiple pallets detected.                                                                                     |
| `configuration/customization/getRack/depthHint`              | An approximate distance (in meters along the X-axis) between the camera and the beam                                                              |
| `configuration/customization/getRack/horizontalDropPosition` | The horizontal drop position of the pallet/load i.e left/right/center of the rack/shelf                                                           |
| `configuration/customization/getRack/verticalDropPosition`   | The vertical drop position of the pallet/load i.e on an empty shelf one or more levels above floor or on floor                                    |
| `configuration/customization/getRack/zHint`                  | The Z-Hint is the approximate expected height (distance in meters along the z-axis) of the front beam with respect to the camera’s optical center |
| `configuration/customization/getRack/clearingVolume`         | Volume to sweep for obstacles with respect to the established origin of the racking system.                                                       |
| `configuration/customization/getItem/depthHint`              | An approximate distance (in meters along the X-axis) between the camera and the item                                                              |
| `configuration/customization/getItem/itemIndex`              | Item index based on the item type                                                                                                                 |
| `configuration/customization/getItem/itemOrder`              | Order of the items detected when multiple items were detected based on the detection score/height.                                                                                     |
| `configuration/customization/volCheck`                       | Minimum and maximum bounding box parameters along X, Y and Z axis                                                                                 |
| `configuration/port/mode`                                    | To designate the measurement range: 2 or 4 meters. This parameter is configurable only in `CONF` state                                            |
| `configuration/port/acquisition/channelValue`                | Channel value where each channel corresponding to a different modulation frequency This parameter is configurable only in `CONF` state            |
| `configuration/port/acquisition/exposureLong`                | Parametrize the long exposure time. This parameter is configurable only in `CONF` state                                                           |
| `configuration/port/acquisition/exposureShort`               | Parametrize the short exposure time. This parameter is configurable only in `CONF` state                                                          |
| `configuration/port/acquisition/offset`                      | Shifts the start point of the measured range. This parameter is configurable only in `CONF` state                                                 |

## State

A PDS application can be configured to either `CONF` or `IDLE` state, implying that there is no `RUN` state. For PDS, the imager will be triggered once a command is issued (akin to [software trigger](../../Technology/3D/triggering.md) for normal camera acquisition).

## Commands

### `nop`
No operation. This is the default command value for PDS application and after processing the given command the value returns to `nop`.

### `getPallet`
Triggers the algorithm to detect the pallet in the camera's field of view. There are three parameters to configure the `getPallet` command.
1. `depthHint`: approximate distance (in meters along the x-axis) that the camera is expected to be away from the pallet, set to **-1** by default to use automatic distance detection. Note that this works best for pallets with full loads and will most likely fail for empty pallets.
2. `palletIndex`: pallet type index. ifm has developed PDS based on standardized pallets (block, stringer or EPAL).
3. `palletOrder`: sets the order of pallets based on their score (height from floor).

:::{note}
For more details, refer to [the `getPallet` documentation](../GetPallet/getPallet.md).
:::

### `getRack`
Triggers the industrial rack recognition algorithm, taking into account the following parameters:
1. `clearingVolume`: The bounding box parameters in the camera's FOV where the position of the rack is expected.
2. `depthHint`: Approximate distance (in meters along the x-axis) that the camera is expected to be away from the rack. The default value is `1.8 m`.
3. `horizontalDropPosition`: Selection of the horizontal drop position. The user must specify the upright to PDS algorithm to detect the pose of a rack.
4. `verticalDropPosition`: Selection of the vertical drop position. The user must specify the drop position for the PDS algorithm.
5. `zHint`: Approximate distance from the center of the coordinate system to the beam of the rack.

:::{note}
For more details, refer to [the `getRack` documentation](../GetRack/getRack.md).
:::

### `getItem`
Triggers the algorithm to find the customized item (for example: Dolly/Trolley). This functionality is only available for certain items. Please contact ifm support to add a customer item. The `getItem` can be configured with following parameters.
1. `depthHint`: Approximate distance (in meters along the x-axis) that the camera is expected to be away from the pallet. By default it is set to **-1** to use an automatic detection of the distance.
2. `itemIndex`: The index of the item type.
3. `itemOrder`: Set the order of detected items (if multiple items are detected) based on their `score`/`height` (height from ground).

:::{note}
For more details, refer to [the `getItem` documentation](../GetItem/getItem.md).
:::

### `volCheck`
Triggers the algorithm to detect the number of valid pixels in a user-defined region of interest.
1. `xMax`: Maximum bounding box dimension of VOI along X-Axis.
2. `xMin`: Minimum bounding box dimension of VOI along X-Axis.
3. `yMax`: Maximum bounding box dimension of VOI along Y-Axis.
4. `yMin`: Minimum bounding box dimension of VOI along Y-Axis.
5. `zMax`: Maximum bounding box dimension of VOI along Z-Axis.
6. `zMin`: Minimum bounding box dimension of VOI along Z-Axis.

:::{note}
For more details, refer to [the `volCheck` documentation](../VolCheck/volCheck.md).
:::