# Symmetry threshold

|Name|Minumim|Maximum|Default
|--|--|--|--|
|Symmetry threshold|0|1|0.4|

## Abstract

The parameter symmetry threshold is mainly used for filtering motion artifacts. Increasing this value leads to more valid pixels around moving objects, but it also increases the motion blur and therefore wrong distance measurements at the edge of the moving object.

## Description

The `O3R-camera-heads` are using the ifm ToF (TimeOfFlight) technology for measuring the distance towards objects. To calculate one single point cloud, the system takes several images. These images are correlated to each other (`ToF correlation images`). This correlation is represented as symmetry.
As lower the value, as higher the symmetry. Due to inherit noise is no perfect symmetry possible.

Decreasing the threshold invalidates more pixel, where the symmetry is higher in deviation. Increasing the threshold validates more pixels, also more noisy pixels in general.
[fast moving object]

Noisy objects/materials also tend to decrease the symmetry. Due to the "jittering" of the values.

## Should you change the symmetry threshold?

There are a few cases, where changing the symmetry threshold might make sense. If you have very low reflective surfaces, and a lot of invalidated pixels. The distance measurements will be of, perhaps even drastically. But perhaps, you like valid pixels with inaccuracy more than invalidated ones. Decreasing the threshold appears to make moving objects better too. But this is an visual illusion. The actual distance values, especially on the edges are far from accurate. It looks like `motion blur`. Again, this might be something you aim for.

You might think, that increasing the value to the maximum (1) is improving your image. It is true, that *bad pixels* will be invalidated. However, at the maximum, more or less all pixels get invalidated at some point. You also do not gain better accuracy with higher setting either. Higher maximum values would help with very noisy objects, but we believe that other filters are better suited for that (min. amplitude, temporal filter, etc.).

## Dependencies/Related topics

Related parameter `Dynamic symmetry`*[Link missing]*