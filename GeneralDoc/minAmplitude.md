# Filter: Minimum Amplitude

| Name | Mininum | Maximum | Default |
| -----|---------:|:---------|:---------:|
| Minimum amplitude | 0 | 1000 | 20 |

## Description

An 3D image taken with the O3R-Camera-Head contains several information. Distance information is the obvious one. But for each pixel, you also get the information about how much light was received. This is the so called `amplitude image`.

[amplitude image]

As you can imagine, if the amplitude value drops to 0, no light was received and therefore no distance measurement was taken. If the amplitude values rises over 1000, the pixel is (over)satured and it also not possible to get any distance information (this happens easily with reflectors).
With the `Minimum amplitude` filter, you can choose the treshold/limit when the system should discard the pixels. Is the amplitude value dropping bellow this threshold, the pixel is shown as `invalid - low amplitude`. You might be tempted, to just set the threshold from the default 20 to 0.

[img amplitude 20 and img amplitude 0]

In certain cases, this might be the right approach. But generally speaking, as lower the amplitude, as more `noisy` and inaccurate is the distance measurement. Have this in mind.

Bad reflecting objects (e.g. black ones) are reflecting less light, and therefore tend to fall easier under the minimum amplitude than bright objects. In this use cases, it might make sense to decrease the minimum amplitude to get some data back. Even, if this data is more noisy than the same data from bright objects.

## Dependencies to other filters

If you decrease the minimum amplitude, we recommend to activate some noise filtering (temporal or adaptive/spatial). This should mitigate the noisier data. We believe, that the temporal filter could be a good choice (see temporal filter).