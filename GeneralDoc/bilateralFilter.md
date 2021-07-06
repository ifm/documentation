# Adaptive noise bilateral filter

|Name|Minumim|Maximum|Default
|--|--|--|--|
TODO: update information from schema

## Abstract
The O3R software allows for filtering the distance image and the dependent point cloud image in the spatial domain. The spatial domain of a 3D image can be thought of as the local neighbourhood in the images pixel coordinates, i. e. row and column coordinates, or the related 3D coordinates, i. e. X-, Y-, and Z-coordinates of the distance image projected into R3 space. Distance information of pixels within a local neighbourhood are combined following the mathematical description of the filter to form a new image with less noise.  

The bilateral filter is the preferred spatial filter. It can be applied with different filter mask sizes which can be set via the parameter `anfFilterSizeDiv2`. For larger filter mask sizes the local noise reduction and flattening is more pronounced. 

## Description

This documentation mainly focuses on the lateral / spatial filtering when using the bilateral filter. This is the prefered spatial filter compared with the spatial median filter as it allows for less 'smearing' of edge information and will presereve edge information better. 

This distance bilateral filter is in concept very similar to a bilateral filter applied to RGB 2D images. Any bilateral filter is a non-linear edge-preserving smoothing filter. It can be thought of as a filter which replaces the value per pixel with a weighted average of the information from nearby pixels. The weighting is a combination of the spatial kernel and the range kernel. The range kernel can be subsituted by a weight based on the distance noise information which is also available as an additional image (see distance noise filter description).  

Such a wighted average is computed by convlution over the spatial domain. The convolution of the original image and the filter mask returns an image of the same size, i. e. ammount of pixels, and is adjusted and continued at the image borders.  

The bilateral filter is controlled by the parameter `anfFilterSizeDiv2`.    
`anfFilterSizeDiv2 = 0` is equivalent to turning the filter off. The image is not filter with the bilateral filter anymore.   
`anfFilterSizeDiv2 = 1` is equivalent to setting the filter mask size to a local 3x3 pixel neighbourhood. TODO insert image of 3 pixel neigbourhood.   
`anfFilterSizeDiv2 = 2` is the highest allow vlaue. It is euqivalent to a filter mask size of 5x5 pixels. TODO insert image of 5 pixel neighbourhood.  

Invalid pixels will be ignored during the filtering process and have therefore no impact on the sourounding pixels. TODO ?Invalid pixels will stay invalid after the filtering?   

TODO: decide which parameters will be made public: `anfSigmaLat` and `anfFactorRangeNoise`. These parameters allow for further finetuning of the bilateral filter.  

A list of related filters and application notes can be found below (TODO: add link)


### `anfFilterSizeDiv2` values example pictures
TODO add pictures for the same static scene with different filter mask sizes
[0 anfFilterSizeDiv2 value] -> off
[1 anfFilterSizeDiv2 value] -> 3x3  
[2 anfFilterSizeDiv2 value] -> 5x5  

### spatial fitering under movement and rotation
[slow moving object (lateral movement)- anfFilterSizeDiv2 = 1]
[fast moving object (lateral movement) - anfFilterSizeDiv2 = 1] 

Add note about relation between lateral movements and rotations and their impact on the ammout the scene changes per timeinterval / frame.


## related filters
+ spatial median filter
+ temporal filtering
+ validation filters
    + min amplitude checks
    + min reflectivity checks

## related application notes