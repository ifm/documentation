# Description of the available images

This document gives a high level overview of the images available for the O3R. Receiving certain images can be turned ON/OFF using the schema mask (INSERT-LINK).

>Note: For more information about the types, sizes and other implementation details, please refer to the ifm3d API documentation (INSERT-LINK).

## Raw Amplitude image and Amplitude image

Each pixel of the amplitude matrix denotes the amount of modulated light (i.e., the light from the camera's active illumination) which is reflected by the appropriate object. Higher values indicate higher signal strengths and thus a lower amount of noise on the corresponding distance measurements. The raw amplitude image is not normalized, which can lead to inhomogeneous image impression if a certain pixel is taken from the short exposure time and some of its neighbors are not. Invalid pixels have a value of zero.

The amplitude image is the normalized image over the different exposure times.


## Distance image (radial)

Each pixel of the distance image denotes the ToF distance measured by the corresponding pixel or group of pixels of the imager, along the respective pixel direction. The distance value is corrected by the camera's calibration, excluding effects caused by multi-path interference and multiple objects contributions (e.g., [mixed pixels](INSERT-LINK)). The reference point is the center of the back of the camera head's housing. Invalid pixels have a value of zero.

## Distance noise (radial)

The distance noise represent the estimated standard deviation of the distance error, in meters for each pixel.
Invalid pixels?

!! Not available in STLBuffer?

## Confidence 
The confidence image give detail about the validity of each pixel and the reason (if any) why it was invalidated. See details [here](INSERT-LINK).

## Reflectivity
The reflectivity image represents the estimated reflectivity in the near infrared spectrum of the objects in the scene.
See also the minimum reflectivity filter (INSERT-LINK).
!!Not available through ifm3d??

## Point cloud (XYZ)
The XYZ image (also called point cloud) is a 3-channel image of the spacial planes X, Y and Z. It uses the Cartesian coordinate system.
?? How is an invalid pixel marked

## Unit vectors
The unit vectors are vectors of size 1 that represent each pixel's direction. They are computed from the intrinsic calibration of the camera and the optical model. They are used in combination with the distance image to compute the point cloud.

## JPEG image
This image is the JPEG-encoded RGB image streamed by the 2D imager, when available.



Questions:
https://polarionsy.intra.ifm/polarion/#/project/O3Rx_01/wiki/Software%20Requirements/SRS%203D%20Computation%20Interface%20_DI_ says that invalid amplitude should be -1?
https://polarionsy.intra.ifm/polarion/#/project/O3Rx_01/workitem?id=O3R-2146 says amp == 0 is invalid

Need to understand better the compressed vs. uncompressed algo output. Which one is visible to user? Can we switch?

Is the "Gray image" a thing for the O3R?

Where is the MASK for choosing what to receive from the O3R in ifm3d?