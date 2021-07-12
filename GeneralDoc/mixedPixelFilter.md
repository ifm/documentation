# mixed pixel filter mode

## Table of contents
- [mixed pixel filter mode](#mixed-pixel-filter-mode)
  * [Table of contents](#table-of-contents)
  * [Abstract](#abstract)
  * [Description](#description)
    + [mixed pixel filter based on angle criterion](#mixed-pixel-filter-based-on-angle-criterion)
    + [mixed pixel filter based on distance criterion](#mixed-pixel-filter-based-on-distance-criterion)
  * [filer effect](#filer-effect)
    + [`mixedPixelFilterMode` values example pictures](#-mixedpixelfiltermode--values-example-pictures)
    + [`mixedPixelFilterMode`: angle criterion finetuning](#-mixedpixelfiltermode---angle-criterion-finetuning)
    + [`mixedPixelFilterMode`: distance criterion finetuning](#-mixedpixelfiltermode---distance-criterion-finetuning)
  * [related filters](#related-filters)
  * [related application notes](#related-application-notes)

## Abstract

The O3R software allows pixel based validation checks for filtering pixels of spatially seperated reflection points. The idea behind this is that spatially isolated pixels (in the distance image or point cloud) are very often a result of a mixed signal from forground and background planes. Such pixels don't represent the distance measrument to either object and lie somewhere inbetween. The `mixedPixelFilterMode` controls two validation methods by is value. `mixedPixelFilterMode = 1` switches to (plane based) angle validation check. `mixedPixelFilterMode = 2` switches to distance based validation check. `mixedPixelFilterMode = 0` switches the filter off completely. No mixed pixel filtering is applied anymore.

**We suggest to use the angle based validation method (`mixedPixelFilterMode = 1`). This filter method produces better results for almost all typical usecases.**


## Description
The `mixedPixelFilterMode` controls two different validation checks.  

**'mixedPixelFilterMode = 1' - angle based validation method**  
The angle based mixed pixel filtering is based around the idea of estimating an angle between the optical ray per pixel and an approximated tangent plane on the object (at this exaxt pixel coordinate). If this difference in angle arguments is larger than the allow angle threshold the pixel is marked as a mixed pixel and invalidated.  

The angle threshold of this filter mode is controlled by the parameter `mixedPixelThresholdRad`. The enclosed angle is scaled in radiant angle arguments. A radial angle argument can easily be converted to degree angle arguments by multiplying it by 180/Pi.

**'mixedPixelFilterMode = 2' - distance based validation method**  
The second version of the `mixedPixelFilterMode` is centered around the idea of comparing distances in a local neighbourhood of a pixel. The distance of the pixel gets tested in horizontal and vertical direction, i. e. row and column, against it's neighbouring pixels distance values. If the distance differences are outside the set near and far distance values and their thresholds, set inside the 'mixedPixelFilterMode = 2`, the pixel is marked as a flying pixel, meaning it is invalidated as a candidate for mixed pixel.

The respective filter distance values and their thresholds are controlled by the parameters: `mixedPixelNearDist`, `mixedPixelFarDist`, `mixedPixelThreshDeltaNear`, and `mixedPixelThreshDeltaFar`. They are currently not easily seen by the end user as they are protected and excluded from the json schema files.

### mixed pixel filter based on angle criterion
"mixedPixelThresholdRad": 
    "type": "number",
    "description": "Threshold given in [rad] for the minimum angle between the surface tangent and the view vector (used if mixedPixelFilterMode=1).",
    "default": 0.15,
    "minimum": 0.0,
    "maximum": 1.57079

### mixed pixel filter based on distance criterion
"mixedPixelNearDist": 
    "type": "number",
    "description": "Near distance [m] for adaptive delta distance threshold (used if mixedPixelFilterMode=2).",
    "default": 1.0,
    "minimum": 0.0,
    "maximum": 9.99,
    "attributes": [ "protected" ]

"mixedPixelFarDist": 
    "type": "number",
    "description": "Far distance [m] for adaptive delta distance threshold (used if mixedPixelFilterMode=2).",
    "default": 4.5,
    "minimum": 0.01,
    "maximum": 10.0,
    "attributes": [ "protected" ]

"mixedPixelThreshDeltaNear": 
    "type": "number",
    "description": "Threshold in [m] for distance deviations in the near field (used if mixedPixelFilterMode=2).",
    "default": 0.018,
    "minimum": 0.0,
    "maximum": 2.0,
    "attributes": [ "protected" ]

"mixedPixelThreshDeltaFar": 
    "type": "number",
    "description": "Threshold in [m] for distance deviations in the far field (used if mixedPixelFilterMode=2).",
    "default": 0.14,
    "minimum": 0.0,
    "maximum": 2.0,
    "attributes": [ "protected" ]



A list of related filters and application notes can be found below: [related filters](related-filters), [related application notes](related-application-notes)  

## filer effect 
### `mixedPixelFilterMode` values example pictures
TODO add pictures for the same static scene with different filter mask sizes  
[0 mixedPixelFilterMode value] -> off  
[1 mixedPixelFilterMode value] -> angle based criterion
[2 mixedPixelFilterMode value] -> distance based criterion

### `mixedPixelFilterMode`: angle criterion finetuning
TODO add pixture and explain the finetuning of the angle threshold `mixedPixelThresholdRad`

### `mixedPixelFilterMode`: distance criterion finetuning
TODO add pixture and explain the finetuning of the distance threshold

## related filters
+ isolated pixel filter
+ further validation filters
    + min amplitude checks
    + min reflectivity checks
    + dynamic symmetry checks
    + cw plausiblity

## related application notes




