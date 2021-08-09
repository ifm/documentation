# Modes

## Description

The O3R has the specificity to provide several measurement ranges: a distance measurement is computed only for a subspace of the scene. Elements *fully* outside of the range are not taken into account and have no impact on the measurement (for instance by causing artifacts like [stray-light](strayLight.md) or [MPI](INSERT-LINK)).

>Note: Objects *very* close of the beginning/end of the measurement range can still have an impact on the measurement.

By default, the O3R provides two measurement ranges: two meters and four meters. These ranges use different frequencies to perform the ToF measurement, and therefore show different characteristics especially in how they are impacted with artifacts. The four meters mode shows higher noise levels than the two meters mode (around twice as much).

## Example

Let's look at a simple scene: three boxes are placed in front of the camera, one, two and three meters away (see image below).
![RGB view of the scene](resources/modes_scene.png)

The table below shows the computed distance measurement in the distance image view and the point cloud view with the two modes available by default:

| Mode| Distance image| Point cloud|
|--|--|--|
| 2m| ![Distance image for the two meter mode](resources/2m_mode_distance.png)| ![Point cloud for the two meter mode](resources/2m_mode_cloud.png)|
| 4m| ![Distance image for the four meter mode](resources/4m_mode_distance.png)| ![Point cloud for the four meter mode](resources/4m_mode_cloud.png)|

The third box, which is 3 meters away from the camera, is outside of the measurement range when using the two meter mode, however it is visible when using the four meter mode.

> Note: Using the [offset](INSERT-LINK) in combination with the mode is interesting and allows for a lot of flexibility in using the coded modulation ToF technology. We encourage you to investigate strategies using multiple modes in combination with offsets (see our [application note](INSERT-LINK) on the topic)

## Related topics
+ [Offset](offset.md)
+ [Basic concepts](basicConcepts.md)
