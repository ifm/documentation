# The confidence image 

The confidence image is accessible as part of the data streamed from the O3R device. This image contains information about the validity of each pixel. If the pixel is invalid, the confidence image explains why is has been invalidated. The values are as follows:

- 1: CONF_INVALID - indicated that the pixel is invalid;
- 2: CONF_SATURATED - the pixel is overexposed/saturated;
- 4: CONF_BADAMBSYM - the symmetry thresholed is crossed;
- 8: CONF_LOWAMP - amplitude lower than the minimum amplitude;
- (16|32): CONF_EXPINDEX - indicates whether the short, medium of long exposure is used for this pixel;
- 4: CONF_EXPSHIFT - ??                         
- 64: CONF_INVALID_RANGE - the pixel is outside of the coded modulation range;
- 128: CONF_SUSPECT_PIXEL - this is a bad pixel on the chip;
- 256: CONF_CAM2WORLD_CLIP - ?
- 512: CONF_EDGEPIXEL - edge pixel provide less accuracy, they are invalidated by default;
- 1024: CONF_CW_PLAUSIBILITY - pixels remaining after shifting the offset, between the camera and the beginning of the shifted range;
- 2048: CONF_REFLECTIVITY - the reflectivity is below the threshold;
- 4096: CONF_DYNAMIC_AMPLITUDE - the pixel is probably part of the halo around a very bright object;
- 16384: CONF_MIXEDPIXEL - the pixel is a mixed pixel, landing partially on the object partially on the background;
- 32768: CONF_ISOLATED - an isolated pixel with random amplitude in an area where no amplitude is measured.