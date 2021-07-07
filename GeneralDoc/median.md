# (distance) median filter

|Name|Minumim|Maximum|Default
|--|--|--|--|
TODO: update information from schema

## Table of contents

## Abstract
The O3R software supports two filters for improving the distance measurements based on filtering in the spatial domain. The spatial domain of a 3D image can be thought of as the local neighbourhood in the images pixel coordinates, i. e. row and column coordinates, or the related 3D coordinates, i. e. X-, Y-, and Z-coordinates of the distance image projected into R3 space. These two filters are the distance median filter and the distace bilateral filter.   
**Please use the bilateral filter instead / in compbination with the median filter. The median filter has undesirable side effects (see below).**

## Description
In the following an overview is given which mostly focusses on the median distance filter separately. The (spatial) median filter is applied to a first estimation of the distance image and also on the a the distance noise image.  

The distance median filter is in it's concept very similar to a [median filter applied to RGB 2D images](https://en.wikipedia.org/wiki/Median_filter). Any median filter is a non-linear edge-preserving smoothing filter. It can be thought of as a filter which replaces the value per pixel by the median of a list containing the information from nearby pixels. This filtering technique is robust, i. e. mostly independent of outliers, and reduces noise while keeping edge information intact.  
The median filter is also applied to the distance noise image, which is an independent image of the (radial) distance image, see [add link to distance noise filter]. The filtered distance noise image output uses a heuristic method.  

The computation is achived by sliding the window in the spatial domain over the previous image. TODO add information about image border handling and resulting image size.

The median filter is controlled by the parameter `medianSizeDiv2`.    
`medianSizeDiv2 = 0` is equivalent to turning the filter off. The image is not filter with the median filter anymore.   
`medianSizeDiv2 = 1` is equivalent to setting the filter mask size to a local 3x3 pixel neighbourhood. TODO insert image of 3 pixel neigbourhood.   
`medianSizeDiv2 = 2` is the highest allow vlaue. It is euqivalent to a filter window size of 5x5 pixels. TODO insert image of 5 pixel neighbourhood.  

Invalid pixels will be ignored during the filtering process and have therefore no impact on the sourounding pixels. Invalid pixels will stay invalid after the filtering, i. e. no hole filling.  

A list of related filters and application notes can be found below: [related filters](related-filters), [related application notes](related-application-notes)  

## filer effect 
### `anfFilterSizeDiv2` values example pictures
TODO add pictures for the same static scene with different filter mask sizes  
[0 medianSizeDiv2 value] -> off  
[1 medianSizeDiv2 value] -> 3x3  
[2 medianSizeDiv2 value] -> 5x5  

### disadvantages of the median filter compared with bilateral filter
TODO add desc and pictures about corner rounding  

### combination of both lateral distance filters
+ combination of both filters
+ TODO: add information about which spatial filter gets processed first - bilateral or median filter  

## related filters
+ spatial bilateral filter
+ temporal filtering
+ validation filters
    + min amplitude checks
    + min reflectivity checks

## related application notes




