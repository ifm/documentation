# Symmetry threshold

|Name|Minumim|Maximum|Default
|--|--|--|--|
|Symmetry threshold|0|1|0.4|

## Abstract

The parameter symmetry threshold is mainly used for filtering motion artifacts. Increasing this value leads to more valid pixels around moving objects, but it also increases the motion blur and therefore wrong distance measurements at the edge of the moving object.

## Description

The `O3R-camera-heads` are using the ifm ToF (TimeOfFlight) technology for measuring the distance towards objects. To calculate one single point cloud, the system takes several images. These images are correlated to each other (`ToF correlation images`). This correlation is represented as symmetry.
As lower the value, as higher the symmetry. Due to inherit noise no perfect symmetry is possible.

Decreasing the threshold invalidates more pixel, where the symmetry is higher in deviation. Increasing the threshold validates more pixels, also more noisy pixels in general.

*[img static object | img fast moving object]*

Noisy objects/materials also tend to decrease the symmetry. Due to the "jittering" of the values.

## Dependencies/Related topics

Related parameter `Dynamic symmetry`*[Link missing]*