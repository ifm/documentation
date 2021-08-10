# The confidence image 

The confidence image is accessible as part of the data streamed from the O3R device. This image contains information about the validity of each pixel. If a pixel is invalid, the confidence image explains why is has been marked as invalid. The values are as follows:

- 1: CONF_INVALID - indicates that the pixel is invalid;
- 2: CONF_SATURATED - the pixel is overexposed/saturated;
- 4: CONF_BADAMBSYM - the pixel had bad symmetry, probably because of motion (see [symmetry threshold](INSERT-LINK));
- 8: CONF_LOWAMP - amplitude lower than the [minimum amplitude](INSERT-LINK), or [distance noise threshold](INSERT-LINK) exceeded;
- (16|32): CONF_EXPINDEX - indicates whether the short, medium or long [exposure](INSERT-LINK) is used for this pixel: expIndex = (v & CONF_EXPINDEX) >> 4 indicates the index of the exposure time used by this pixel where low indices indicate shorter exposures;                       
- 64: CONF_INVALID_RANGE - the pixel is outside of the [measurement range](INSERT-LINK);
- 128: CONF_SUSPECT_PIXEL - this is a bad pixel on the chip;
- 256: RESERVED
- 512: CONF_EDGEPIXEL - edge pixels refer to the image edges which are sometimes invalidated by lateral filters;
- 1024: CONF_UNPLAUSIBLE - pixels remaining after shifting the [offset](INSERT-LINK), between the camera and the beginning of the shifted range;
- 2048: CONF_REFLECTIVITY - the [reflectivity](INSERT-LINK) is below the threshold;
- 4096: CONF_DYNAMIC_AMPLITUDE - the pixel is probably part of the halo around a very bright object (see the [dynamic amplitude threshold](INSERT-LINK) and the [stray-light filter](INSERT-LINK));
- 16384: CONF_MIXEDPIXEL - the pixel is a [mixed pixel](INSERT-LINK), part of which is measuring the object and the other part the background;
- 32768: CONF_ISOLATED - an isolated pixel with random amplitude in an area where no amplitude is measured.