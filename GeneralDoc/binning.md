# (pixel) binning

## Table of contents
- [(pixel) binning](#-pixel--binning)
  * [Table of contents](#table-of-contents)
  * [Abstract](#abstract)
  * [Description](#description)
    + [advantages of binning](#advantages-of-binning)
    + [disadvantages of binning](#disadvantages-of-binning)
  * [related filters](#related-filters)
  * [related application notes](#related-application-notes)

## Abstract
The O3r software allows a interpolation / downsampling algorithms via the combination of measurement values per pixel for all available images. This interpolation is done on a pixel per pixel basis and allows the user to reduce the data stream sizes while at the same time improving the image quality towards a more robust measurement value. The `binning` mode is only (currently ?) available for the VGA heads.

One may notice the change in number of pixels the easiest when looking at the amplitude image, distance image and point cloud. They will appear to have less densely spaced image points. The change in number of pixels correlates with the spatial resolution. At a fixed distance the resolution will decrease when combining distance values. When comparing against other camera models and heads the spatial resolution also heavily depend on the their different field of views (FOV) and not only on their number of pixels, e. g. 38k pixels and VGA - 307k pixels.


## Description

This document focusses mainly on describing the process of and related filter parameters for accessing the binning mode for the O3R camera platform. To understand descriptions about possible scenarios and applications where a binning mode can make sense in your application see TODO add link to related application notes.  

The O3R hardware and software can supply all of the following images:  
+ (radial) distance image
+ distance noise image: TODO add link to desc
+ amplitude images: normalized and non-normalized: add link to amplitude filtering
+ reflectivity image
+ confidence image
+ point cloud: X, Y, Z coordinate values in 3 dimensional space
These images are resampled to the same sampling interval, meaning image size and spatial resolution, when the filter `binning` is activated.

The `binning` filter is controlled via a single filter parameter. Allowed filter parameter values are:  
[`binning = 0`] no resampling: the user gets the true image resultion. *Do we ever mention that the VGA imager gets upsampled from a half VGA resolution towards a customer*    
[`binning = 1`] resampling of the VGA imager signal to a `240 x 320` pixel grid.    
  
TODO: add example pictures with and without binning:      
![binning_0](./resources/binning_0.png "image representation VGA image without binning")    
![binning_1](./resources/binning_1.png "image representation VGA image with binning")     

A list of related filters and application notes can be found below: [related filters](related-filters), [related application notes](related-application-notes)

### advantages of binning
Combining (binning) a neighborhood of `2x2` pixels into one measurement value has two distinct advantages:  
1. The point cloud quality will be improved and distance measurements (and other measured values) for uncertain pixels can be improved by combining it with it's neighbors. This for example can be seen in the distance noise image. 
2. The data stream size and bandwidth will be reduced. This is important when running computationally heavy application.
3. Because of the reduced stream size the required network bandwidth is also reduced. A simple `2x2` binning reduces the file size and therefore band with by a factor of 4.   
TODO: continue list

### disadvantages of binning
1. Spatial resolution will be reduced. For applications which focus only on a image region of interest (ROI) instead of the whole image the highest possible spatial resolution might be necessary. Binning and ROI selection are opposed image manipulation strategies.  
TODO: continue list

## related filters
+ spatial filtering
+ temporal filtering
+ validation filters
    + min amplitude checks
    + min reflectivity checks

## related application notes
+ framerates and bandwidth limitations: reduce data flow