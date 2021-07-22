# Minimum Amplitude
## Abstract

The `Minimum amplitude` (`diParam.minAmplitude`) parameter invalidates pixels where the amplitude (reflected light) drops bellow the minimum threshold.

## Description

For each pixel, the amplitude value represents how much light was received by the imager. The `minimum amplitude` parameter provides a threshold defining when the system should discard the low amplitude pixels. The images below show the amplitude image and the point cloud for a scene containing black totes. The totes are made out of a dark plastic and reflect very little light. We can see that part of the point cloud is missing where the amplitude is below the threshold.

|Amplitude image |Point cloud |
|--|--|
|![default-values-amplitude](./resources/default_value_amp.png "3D amplitude image")|![default-values-3d](./resources/default_value_3D.png "3D point cloud with default values")|

Now let's see what happens when we change this threshold value. In the table below, we display the same scene measured with different amplitude thresholds. We can see that with a value of 0, we are able to compute the point cloud for the very dark areas. On the other hand, when we increase the threshold to 50, a large part of the point cloud is lost.

|Minimum amplitude| Point cloud|
|:-:|-|
|0|![min-a,p-0-3d](./resources/amp_0_3D.png "3D point cloud with minimum amplitude 0 values")|
|20|![min-a,p-0-3d](./resources/default_value_3D.png "3D point cloud with minimum amplitude 0 values")|
|50|![min-a,p-0-3d](./resources/amp_50_3D.png "3D point cloud with minimum amplitude 0 values")|

In certain cases, for instance when black objects are in the field-of-view, changing the default value from 20 to 0 can be beneficial as more pixels are valid, leading to a more complete point cloud. Generally speaking however, lowering the amplitude leads to more ambient noise and less accuracy is the distance measurement. In this case we encourage you to test the [filters](parameters.md) available with the O3R to mitigate the noise that exists for black objects measurements.

> Note: black objects in the visible spectrum are not necessarily black in the near infrared range.

> Note: The minimum amplitude threshold is applied to the *non-normalized* amplitude image. The numerical value of the *normalized* amplitude image (the one you receive) might not correspond to expected values with the set threshold. 

## Related topics

The minimum amplitude parameter is related to the maximum distance noise parameter: a low amplitude value together with a high distance noise value ensures that more pixels are valid but will allow for a noisier measurement, requiring some filtering for instance with the temporal filter. See following:
- [Distance noise](maxDistNoise.md)
- [Temporal filter](INSERT-LINK)