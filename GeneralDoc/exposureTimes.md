# Exposure times

## Description
The exposure time designates the amount of time during which the illumination device sends light out in the scene. The longer the exposure time, the more light illuminates the scene and the more light is reflected back to the camera.

The proper exposure time for a specific scene depends on the dynamics of the scene (combination of dark and light area, close and far away objects, mobile or stationary objects). A single exposure time usually cannot properly expose all the areas of the scene (the dark areas might be under-exposed, or the bright areas over-exposed).

To palliate this issue, the O3R combines three exposure times for computing a single distance measurement:
- A long exposure time, set with the `expLong` parameter, handles the darkest areas of the scene,
- A short exposure time, set with `expShort` handles the brighter areas of the scene,
- A very short exposure time (currently fixed at 30us) is used to get proposer exposure of very bright objects like reflectors in the close range.

The default values of the exposure times fit most scenes, but might need to be adjusted up or down for very high contrast scenes.

### Exposure index in the confidence image
The [confidence image](confidenceImage.md) indicates which exposure time is used for specific areas of the scene.

*IMAGES COMING SOON*

### Dark objects and temporal filter
Dark objects (in the IR spectrum) can be tricky to detect properly even with the maximum exposure time of 5000us for `expLong`. In this case, we recommend using the [temporal filter](INSERT-LINK) as it helps collect more data for dark areas and reduces noise in said areas.
