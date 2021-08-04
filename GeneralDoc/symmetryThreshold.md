# Symmetry threshold
## Abstract

The symmetry threshold `maxSymmetry` is used for filtering motion artifacts. Increasing the threshold value, equivalent to decreasing the filter strength, leads to more valid pixels around moving objects, but can also increases the chance of computing wrong distance measurements for some pixels. Decreasing the threshold value, equivalent to increasing the filter strength, will results in invalidating more pixels by means of their estimated symmetry, meaning more pixels will we invalidated for the whole scene. 
This filter is controlled by two parameters: `enableDynamicSymmetry` this boolean value will enable / disable any symmetry based filtering, and `dynamicSymmetryThreshold` is it respective threshold for finetuning the filter strength.  

## Description
The O3R camera heads are using the ifm ToF (Time Of Flight) technology for measuring the distance to objects. To calculate one single point cloud image, the system takes several independent image frames. These images are correlated over time (see [basic concepts](INSERT-LINK)). This correlation is represented as symmetry value (it can be though of as the four modulated signals, used for performing the *raw* measurement, being more or less symmetrical to each other). 

For low symmetry threshold values, only pixels where the correlation images are highly symmetrical , e.g. no or little motion artifacts) are valid. Due to inherent noise, a perfect symmetry is never possible even for static scenes. Increasing the symmetry threshold validates more pixels including noisy pixels and potential motion artifacts. This might be somewhat counter intuitive to your interpretation of a filter threshold value. Just think in symmetry values required to be high instead of filter strenght.  

In high-noise environment, it can happen, that the sensor noise gets propagated to the symmetry image. Most of the pixels are invalidated due to the symmetry threshold. In these cases, the dynamic symmetry should be activated. The dynamic symmetry ensures that the symmetry threshold of a pixel is at least high enough to prevent invalidation due to sensor noise. It can be thought of as differentiating motion artifacts from ambient noise in the scene.

*If the dynamic symmetry is enabled, each pixel gets its individual symmetry threshold, which is either the `maxSymmetry` setting or the expected symmetry (computed internally) due to noise, whichever one is larger.*

## Example

*COMING SOON...*