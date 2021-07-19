# CW plausiblilzation

## Table of contents
- [CW plausiblilzation](#cw-plausiblilzation)
  * [Table of contents](#table-of-contents)
  * [Abstract](#abstract)
  * [Description](#description)
    + [`anfFilterSizeDiv2` values example pictures](#-anffiltersizediv2--values-example-pictures)
  * [related filters](#related-filters)
  * [related application notes](#related-application-notes)


## Abstract

The O3R software allows for filtering it's measured distance values (and dependent images) based on a validity check against a measurement in a separate frequency spectrum with standard continous wave (cw) time of flight (TOF). This validity check allows the possilbilit to discard near-distance pixels wich are suspected to be non robust distance measurements and lay before the start of the actual requested measuring range.  

## Description

The cw plausibilization filter is not a filter which should typically be used by the enduser at the start of a parameter finetuning for their own application. Please start with other filters such as termporal filter, spatial filter, and other validity checks such as dynamic symmetry, dyamic amplitude and TODO add more.

The two parameters for finetuning the cw plausibilization are: `cwPlausibilityThresholdRatio` and `cwPlausibilityMinAmp`. Both work on a amplitude based comparison against the set thresholds.
`cwPlausibilityThresholdRatio`  is a simple threshold for comparing the two modulation strategies. At `cwPlausibilityThresholdRatio = 0` the whole cw plausibilization is disabled. The second parameter `cwPlausibilityMinAmp` checks the ammount of received light of the cw TOF measurment. If this value is lower than the selected `cwPlausibilityThresholdRatio` the pixel is discareded as well. See the *TODO add link documentation on min amplitude checks* to find a more detailed description of amplitude values and their meaning. Both tests have to be met at the same time, a single pass does not suffice.

A list of related filters and application notes can be found below: [related filters](related-filters), [related application notes](related-application-notes)


### `anfFilterSizeDiv2` values example pictures
In the following a few example pictures are shown where the effect of the different  cw plausibilization settings (mainly switch cw plausibilization on and off) are compared:  

Add example pictures with / without distance measurents pixels in the foreground: 

![cw_plausibility_on](./resources/cw_plausibility_on.png "3D point cloud with cw plausibilization") 
![cw_plausibility_on_img](./resources/cw_plausibility_on_img.png "distance and amplitude images with cw plausibilization")  

![cw_plausibility_off](./resources/cw_plausibility_off.png "3D point cloud without cw plausibilization")  
![cw_plausibility_off_img](./resources/cw_plausibility_off_img.png "distance and amplitude images without cw plausibilization")


## related filters
+ validation filters
    + min amplitude checks
    + min reflectivity checks

## related application notes