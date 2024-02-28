# Camera calibration for PDS

The PDS application always returns the position of an object with respect to the calibrated coordinate system. Typically, the calibrated coordinate system corresponds to the fork tines, so that the coordinate system will go up and down with the forks and the pallet position will always be provided with reference to the current position of the forks.

## Concepts

PDS expects the orientation of the coordinate frame to be as follows:
- X is pointing in direction of the forks,
- Y is pointing to the left of the forks,
- Z is pointing up.

When uncalibrated, the camera coordinate system is such that Z is pointing away from the camera, and X is pointing away from the cables. This is represented in the image below:

![Uncalibrated camera coordinate system](resources/default_camera_coord_sys.png)

The uncalibrated coordinate system does not correspond to what PDS expects. Consequently, if no calibration is set, PDS will raise an error.

To fit the expected coordinate system of PDS, the coordinate system has to be rotated. An example of a correctly calibrated coordinate system would be as shown in the image below, where the origin of the coordinate system is place at the center of the base of the forks:

![Coordinate system calibrated to the center of the base of the forks](resources/forks_base_center_coord_sys.png)

Note that the user can decide where to place the origin of the coordinate system. We show a couple examples [below](#examples).

PDS will look for a pallet within a defined volume of interest. By default, it expects the camera to be placed between 22 and 35 cm above the bottom plane of the pallet. 
TODO: add details about the VOI, understand how VOI changes with calibration.

Note that errors in the camera calibration will lead to errors in the position of the targeted object. If CAD data is known to be precise enough, it can be used to extract calibration values for the camera. Otherwise, any of [the calibration methods](/SoftwareInterfaces/Toolbox/ExtrinsicCalibration/README.md) provided by ifm can be used.

## Examples

### Horizontally mounted camera, tip of fork coordinate system
Let's take for example a camera mounted horizontally, looking straight ahead, directly between the two forks. 
Let's assume the fork tines coordinate system's origin is at the tip of the right fork, like shown in the image below:
![Coordinate system calibrated to the tip of the right fork](resources/forks_tips_coord_sys.png)

Let's also assume the following measurements:

![Translation values from the camera to the tip of the right fork](resources/translations_to_fork_tip.png)

Then, the values for the rotation and translations are as follows, shown in the Vision Assistant calibration wizard:

![Calibration values for the tip of fork example](resources/calibration_values_fork_tips.png)

This is equivalent to setting the following parameters in the relevant port's JSON configuration:
```json
{
    "ports":{
        "portX":{
            "processing":{
                "extrinsicHeadToUser":{
                    {
                        "rotX": 0,
                        "rotY": 1.57,
                        "rotZ": -1.57,
                        "transX": 1.00,
                        "transY": 0.25,
                        "transZ": 0.05
                    }
                }
            }
        }
    }
}
```
### Other example