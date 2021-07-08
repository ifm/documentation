# mixed pixel filter mode

|Name|Minumim|Maximum|Default
|--|--|--|--|
| mixedPixelFilterMode | 0 | 2 | 1 |

## Table of contents

## Abstract

The O3R software allows pixel based validation checks for filtering spatial seperated points / pixels. The idea behind is that spatially isolated pixels are very often a result of a mixed signal from forground and background planes. Such pixels don't represent either of the objects and lie some where inbetween. The `mixedPixelFilterMode` controls two validation methods by is value. `mixedPixelFilterMode = 1` switches to (plane based) angle validation check. `mixedPixelFilterMode = 2` switches to distance based validation check. Both exist on a local neighbourhood of the pixel in question. `mixedPixelFilterMode = 0` switches the filter off completely. No mixed pixel filtering is applied anymore.


## Description

TODO: add a more indepth description

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




