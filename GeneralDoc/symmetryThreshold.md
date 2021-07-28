# Symmetry threshold
## Abstract

The symmetry threshold `maxSymmetry` is used for filtering motion artifacts. Increasing this value leads to more valid pixels around moving objects, but it also increases the chances of computing wrong distance measurements for some pixels in the scene. In cases with a high ambient noise level, the dynamic symmetry should be enabled (with the parameter `enableDynamicSymmetry`) to ensure pixels are not invalidated due to ambient noise.

## Description

The O3R camera heads are using the ifm ToF (Time Of Flight) technology for measuring the distance to objects. To calculate one single point cloud, the system takes several images. These images are correlated to each other (see [basic concepts](INSERT-LINK)). This correlation is represented as symmetry (it can be though of as the four modulated signals used for performing the *raw* measurement being more or less symmetrical to each other). 
If a low symmetry threshold value is set, only the pixels where the correlation images are highly symmetrical (no or little motion artifacts) are valid. Due to inherent noise, no perfect symmetry is possible. 
Increasing the symmetry threshold validates more pixels including noisy pixels and potential motion artifacts.

In high-noise environment, it happens that, the sensor noise being propagated to the symmetry, most of the pixels are invalidated due to the symmetry threshold. In these cases, the dynamic symmetry should be activated. The dynamic symmetry ensures that the symmetry threshold of a pixel is at least high enough to prevent invalidation due to sensor noise. It can be thought of as differentiating motion artifacts from ambient noise in the scene.

If the dynamic symmetry is enabled, each pixel gets its individual symmetry threshold, which is either the `maxSymmetry` setting or the expected symmetry (computed internally) due to noise, whichever one is larger.


## Example
*[img static object | img fast moving object]*
