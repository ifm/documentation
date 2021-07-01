# Parameter: Minimum Amplitude

| Name | Minimum | Maximum | Default |
| -----|---------:|:---------|:---------:|
| Minimum amplitude | 0 | 1000 | 20 |

## Abstract

The `Minimum amplitude` parameter invalidates pixels where the amplitude (reflected light) drops bellow the minimum threshold.

## Description

An 3D image taken with the O3R-Camera-Head contains several information. Distance information is one, but also amplitude. For each pixel, the amplitude value represents about how much light was received. This kind of image is called `amplitude image`.

[amplitude image]

If the amplitude value drops to 0, no light was received and therefore no distance measurement was taken. If the amplitude values rises over 1000, the pixel is oversatured and it is impossible to get any distance information (this happens easily with reflectors).
The `Minimum amplitude` parameter,provides a threshold/limit when the system should discard the pixels. Is the amplitude value dropping bellow this threshold, the pixel is shown as `invalid - low amplitude`. 

[img amplitude 20 and img amplitude 0]

In certain cases, changing the default value form 20 to 0 could be beneficial. Generally speaking, as lower the amplitude as more `noisy` and inaccurate is the distance measurement.

Bad reflecting objects (e.g. black ones) are reflecting less light, and therefore tend to fall easier under the minimum amplitude than bright objects. In this use cases, it might be beneficial to decrease the minimum amplitude to get some data back. Even, if this data is more noisy than the same data from bright objects.

## Dependencies to other filters

It is recommended to activate some noise filtering (temporal or adaptive/spatial), if the minimum amplitude threshold is decreased. This should mitigate the noisier data.