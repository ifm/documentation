# Maximum distance noise
## Abstract

The O3R software estimates distance noise per pixel in addition to the distance information per pixel. This distance noise parameter is an estimation of the standard deviation of the radial distance measurement, given in meters. It is based on a noise model built upon the acquired time of flight (ToF) measurements of a single frame. Pixels with a noise value above the threshold `maxDistNoise` are invalidated.


## Description
The O3R camera and software uses the ifm ToF technology for measuring the distance of objects per pixel. The result is a distance image as well as a distance noise image. The distance noise deduction can be interpreted as a standard deviation of the distance measurement in a metric scale. The noise level is dependent on the received signal's amplitude (lower amplitude means greater noise) and on the ambient light level (high ambient light level, especially sunlight, can lead to high noise level). 

The distance noise image gets processed in the same algorithmic pipeline as the distance image itself. Any filter applied to the distance image are applied to the distance noise image as well. For example if filters are activated in the spatial domain (see the [bilateral filter](INSERT-LINK)), they also filter the distance noise image, such that the adapted noise image reflects the lowered noise due to lateral filtering.

The parameter `maxDistNoise` is used to invalidate pixels with high noise levels. Higher `maxDistNoise` values will allow more noisy pixels to be  valid pixels in the point cloud. The maximum allowed value is 1 meter, though we do not recommend using such a high value as the resulting distance measurement will be highly inaccurate in the noisy areas. 
Low `maxDistNoise` values will result in more noisy pixels being marked as invalid. Using values lower than 0.01 meters is not recommended either as it invalidates large portions of the image for many scenes (we expect a distance standard deviation of about 0.5 percent of the measurement range, see the [datasheets](INSERT-LINK)).    

The minimum allowed `maxDistNoise` value is 0.00 meters. This will switch off the validation process based on the estimated distance noise image. The distance noise image is still computed and available to the user.

We suggest to start your experiments with the default values and assess the point cloud quality for your specific use case. The current default value is set to 0.02 meters, which allows for a robust point cloud with negligible noise. For applications where a rich point cloud (i.e., more valid pixels) is preferred over accuracy, increasing the noise threshold can be a good idea.

### Example
The following table shows the measurement for a same scene with two different distance noise threshold values. The scene consists of a box positioned one meter away from the camera, outside in full sunlight. The amount of noise due to the ambient light is high, but we see that we can still get distance values for many pixels by increasing the noise threshold.

| Noise threshold [m]| Distance noise image| | Point cloud|
|:--:|--|--|--|
| 0.01| ![Low noise threshold - noise image](resources/low_noise_001_outside_noise.png)| ![Color bar](resources/color_bar_noise.png)| ![Low noise threshold in the point cloud](resources/low_noise_001_outside_cloud.png)|
| 0.07 | | | ![Low noise threshold in the point cloud](resources/med_noise_007_outside_cloud.png)|

> Note: the distance noise image is the same for both noise threshold value. The difference is viewed in the point cloud, where more or less pixels are discarded by the noise filtering.

## Related topics
+ [Bilateral filter](INSERT-LINK) (see also the [median filter](INSERT-LINK))
+ [Temporal filter](INSERT-LINK)
+ [Minimum amplitude](INSERT-LINK)
+ [Minimum reflectivity](INSERT-LINK)
