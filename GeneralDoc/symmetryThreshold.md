# Symmetry threshold

|Name|Minumim|Maximum|Default
|--|--|--|--|
|Symmetry threshold|0|1|0.4|

## Description

The `O3R-camera-heads` are using the ifm ToF (TimeOfFlight) technology for measuring the distance towards objects. There are several ways to measure distance with ToF. You could send out single impulses (LIDAR), or you can use a continuos wave (ifm approach).
As you can imagine, different approaches come with different advantages/disadvantages.

The imager uses actually 4 phases, to measure the distance. You basically have 4 measurement points. These points, have a symmetry to each other, due to the continuos modulation we use. Of course, there are some tolerances and it is never perfect. But if this symmetry decreases to much, we invalidate the pixel where this happens.
These four phases are done not in parallel but sequential.

Imagine following scenario: The object you measure has a clear edge (like a box). If the object does not move around, several pixels hit the edge and several hit the background etc. All four measurement phases hit their respective "target" and the system reaches a high symmetry. Now the objects starts to move (e.g. on a conveyor belt). Remember, the 4 phases are measured after each other. What happens, if 2 phases hit the edge of the box - and due to the moving of the box - 2 hit the background? The symmetry value goes down, up to the point where the pixel is invalidated. As faster the object is moving, as more pixel around the edges get invalidated. This is the reason, why fast moving objects have something like an "aura/shadow" around them. Try waving your hand very fast in front of the camera to see that effect. 

[fast moving object]

Of course, higher framerate and lower exposure time settings improve this behavior.
Very noisy objects/materials also tend to decrease the symmetry. Due to the "jittering" of the values.

## Should you change the symmetry threshold?

There are a few cases, where changing the symmetry threshold might make sense. If you have very low reflective surfaces, and a lot of invalidated pixels. The distance measurements will be of, perhaps even drastically. But perhaps, you like valid pixels with inaccuracy more than invalidated ones. Decreasing the threshold appears to make moving objects better too. But this is an visual illusion. The actual distance values, especially on the edges are far from accurate. It looks like `motion blur`. Again, this might be something you aim for.

You might think, that increasing the value to the maximum (1) is improving your image. It is true, that *bad pixels* will be invalidated. However, at the maximum, more or less all pixels get invalidated at some point. You also do not gain better accuracy with higher setting either. Higher maximum values would help with very noisy objects, but we believe that other filters are better suited for that (min. amplitude, temporal filter, etc.).