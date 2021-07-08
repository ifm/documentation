
# isolated pixel filter

|Name|Minumim|Maximum|Default
|--|--|--|--|
| isolatedPxFilterMaxValid3x3 | 1 | 9 | 5 |


## Table of contents
* [Abstract](#abstract)
* [Description](#description)
* [filer effect](#filer-effect)
    + [`mixedPixelFilterMode` values example pictures](#-mixedpixelfiltermode--values-example-pictures)
* [related filters](#related-filters)
* [related application notes](#related-application-notes)


## Abstract

The O3R software allows pixel based validation checks for filtering locally isolated pixels. This concept of locally isolated pixel is very sililar to the mixed pixel filter. The difference in the areal criterions is their neighbourhood. For the `isolatedPxFilterMaxValid3x3` filter mode only a 3x3 PIXEL neighborhood is eamined (compared to a true spatial relation in R3 for the `mixedPixelFilterMode`).  

**If you are looking for a filter comparable to what is commonly known as a flying pixel eraser, please see the documenation of the mixed pixel filter TODO add link to mixed pixel filter.**  


## Description

TODO add description and picture about a 3x3 pixel neighbourhood  
TODO add description about this counting criterion: where's the counting started / how is the filter implemented as recursive application without introducing a bias to the image   

TODO Hole extrapolation and invalidity criterion combination  
TODO mention the position in filter pipeline  
 
isolatedPxFilterMaxValid3x3  
"isolatedPxFilterMaxValid3x3":   
    "type": "integer",
    "description": "Valid pixels need at least this amount of valid neighbors (including the center pixel); 1: disable the check",
    "default": 5,
    "minimum": 1,
    "maximum": 9,
    "attributes": [ "protected" ]  

## filer effect 
### `mixedPixelFilterMode` values example pictures
TODO add pictures for the same static scene with different counters on the 3x3 mask   

TODO brainstorm applications  

## related filters
+ mixed pixel filter
+ further validation filters
    + min amplitude checks
    + min reflectivity checks
    + dynamic symmetry checks
    + cw plausiblity

## related application notes