# Description of the available images

**INTERNAL:** Relevant polarion doc:
https://polarionsy.intra.ifm/polarion/#/project/O3Rx_01/wiki/Software%20Requirements/SRS%20Process%20Communication%20Interface%20Component%20PCIC
https://polarionsy.intra.ifm/polarion/#/project/O3Rx_01/workitem?id=O3R-2146
https://polarionsy.intra.ifm/polarion/#/project/O3Rx_01/workitem?id=O3R-3125


>Note: the width and height of each image depends on the imager type. For the 38k imager, the width is 224 pixels and the height 172 pixels.

>Note: All information is stored in little endian
## Amplitude image
| Image| Size| Type| Unit|
|--|--|--|--|
| Amplitude| width*height| 16 bit unsigned integer| NA|

Each pixel of the amplitude matrix denotes the amount of modulated light (i.e., the light from the camera's active illumination) which is reflected by the appropriate object. Higher values indicate higher PMD signal strengths and thus a lower amount of noise on the corresponding distance measurements. The amplitude value is directly derived from the PMD phase measurements without normalization to exposure time. In multiple exposure mode, the lack of normalization may lead (depending on the chosen exposure times) to inhomogeneous amplitude image impression, if the a certain pixel is taken from the short exposure time and some of its neighbors are not. Invalid pixels have a value of zero.

**INTERNAL:** Link to polarion description https://polarionsy.intra.ifm/polarion/#/project/o3d300_01/workitem?id=660606-3972

## Distance image (radial)

| Image| Size| Type| Unit|
|--|--|--|--|
| Distance| width * height| 16 bits unsigned int| millimeters|

Each pixel of the distance matrix denotes the ToF distance measured by the corresponding pixel or group of pixels of the imager. The distance value is corrected by the camera's calibration, excluding effects caused by [MPI](INSERT-LINK) and multiple objects contributions (e.g., [mixed pixels](INSERT-LINK)). The reference point is the optical center of the camera inside the camera housing. Invalid pixels have a value of zero.

## Distance noise (radial)

## Confidence 

## Reflectivity

## Point cloud (XYZ)