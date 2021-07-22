# mixed pixel filter mode

* [Abstract](#abstract)
* [Description](#description)
  + [Angle based validation method](#angle-based-validation-method)
  + [Distance based validation method](#distance-based-validation-method)
* [Examples](#examples)
  + [Different mixed pixel modes](#different-mixed-pixel-modes)
  + [Fine-tuning the angle based method](#fine-tuning-the-angle-based-method)
* [Related topics](#related-topics)


## Abstract

The mixed pixel filter removes spatially isolated pixels. We call these pixels mixed pixels as they result from a mixed signal from foreground and background planes. Such pixels don't represent the distance measurement to either object and lie somewhere in between (they appear to be *flying*, and we sometimes refer to them as *flying pixels*). The `mixedPixelFilterMode` setting defines whether this filter is activated and which validation methods is used. `mixedPixelFilterMode = 1` switches to angle validation check. `mixedPixelFilterMode = 2` switches to distance based validation check. `mixedPixelFilterMode = 0` switches the filter off completely.

**We suggest to use the angle based validation method (`mixedPixelFilterMode = 1`). This filter method produces better results for almost all typical use-cases.**


## Description
The `mixedPixelFilterMode` controls two different methods for invalidation mixed pixels.  

### Angle based validation method  
The angle based mixed pixel filtering (`mixedPixelFilterMode = 1`) is based on the idea of estimating, for each pixel, the angle between the optical and an approximate tangent plane on the object (at this exact pixel coordinate). If the angle difference is larger than the allowed angle threshold, the pixel is invalidated.  
The angle threshold of this mode is controlled by the parameter `mixedPixelThresholdRad` (angle in radians).

### Distance based validation method
The second version of the mixed pixel (`mixedPixelFilterMode = 2`) filter is centered around the idea of comparing distances in the local neighborhood of a pixel. The distance of the pixel is compared in horizontal and vertical direction against its neighboring pixels' distance values. If the distance differences are outside a threshold (set internally), the pixel is invalidated.

## Examples
### Different mixed pixel modes

TODO add pictures for the same static scene with different filter mask sizes  
[0 mixedPixelFilterMode value] -> off  
[1 mixedPixelFilterMode value] -> angle based criterion
[2 mixedPixelFilterMode value] -> distance based criterion

### Fine-tuning the angle based method
TODO add picture and explain the finetuning of the angle threshold `mixedPixelThresholdRad`

## Related topics
+ further validation filters
    + min amplitude checks
    + min reflectivity checks
    + dynamic symmetry checks
    + cw plausiblity




