# maximum distance noise
|Name|Minumim|Maximum|Default
|--|--|--|--|
TODO: update information from schema

## Abstract

The O3R software estimates distance information per pixel and a related distance noise paramemter per pixel as well. This distance noise parameter is an esitmator of the standard deviation of the (curved) radial distance measurement in meters. It is based on noise estimation via redundant information of mutltiexposure for each frame. Based on the threshold value `maxDistNoise` pixels are marked as invalid.


## Description
The `O3R-camera-heads` use the ifm ToF (TimeOfFlight) technology for measuring the distance of objects per pixel. The ifm approach is to measure distance by substituting it as a time related measure. 
The standard recording modes (TODO: add link to mode overview and e.g. 4m high mode) uses four independent measurements per exposure to estimate the distance per pixel. Therefore at least four indpendent measurement points exist per pixel. These measurement points allow for a noise deduction among other values. The distance noise deduction can be interpreted as a standard deviation of the distance measurment in a metric scale.  

The resulting distance noise image gets processed in the same algorithmic pipeline as the distance image itself. Any filter applied to the distance image are applied to the distance noise image as well. For example if filters are activated in the spatial domain (TODO: add reference to median filter), they filter the distance noise image with the same filter parameters.  

In a last step the parameter `maxDistNoise` is used as a threshold for marking pixels as valid or invalid based on their estimated noise and the filter threshold. The distance noise filter is controlled by this single value. Larger `maxDistNoise` values will allow more noisy pixels to still end up beeing valid pixels. The maximum allow value is "1" meter. Using such high values is not recommended. Lower `maxDistNoise` values will result in more pixels beeing marked as invalid. The minumum is "0.00" meters. "0.00" meters "maxDistNoise" is not recommended either and sould be used with care as it invalidates almost the whole picture for many scenes, i. e. geometric configurations.   

A list of related filters and application notes can be found below (TODO: add link)

### `maxDistNoise` threshold values example pictures
TODO add pictures for the same static scene with different threshold values
[low maxDistNoise value] -> 0.01  
[medium maxDistNoise value] -> 0.05  
[high maxDistNoise value] -> 0.2  

### distance noise estimaiton under movement and rotation

[slow moving object (lateral movement)- low maxDistNoise value] -> 0.02  
[fast moving object (lateral movement) - high maxDistNoise value] -> 0.15  

Add note about relation between lateral movements and rotations and their impact on the ammout the scene changes per timeinterval / frame

### distance noise estimation for black objects
TODO add



## Should you change the `maxDistNoise` value?
The user may think that a simple change of the `maxDistNoise` value will improve the point cloud. This is true for us humans who can interprete a point cloud and distance image quite easily even though it may appear a bit more noisy. This however is not always true for robots and their post processing algorithms. The tradeoff between many pixels, i. e. a rich point cloud, and a more robust point cloud, i. e. only more reliable pixels, is part of the finetuning for each application.  

We suugest to start with the default values. The default is currently set to ``0.02` meters. This value was chosen leaning more towards a rich point cloud for static scences with few artefacts. This might not be true for all customer applications. Please also keep in mind that `maxDistNoise` threshold works in connection and relation with other filters as mentioned above.

## related filters
+ spatial filtering
+ temporal filtering
+ min amplitude checks
+ min reflectivity checks

## related application notes