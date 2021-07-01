*Disclaimer: As a vendor of industrial equipment, we always try to mitigate physics artifacts to the best of our abilities. The default settings are chosen with this goal in mind: providing the best experience for **most** cases. However, the variety of scenes that mobile robots and other applications can encounter makes a "one-fits-all" configuration impossible. With this in mind, we present in our Application Notes the outliers, challenging but common cases that might require fine tuning of the camera configuration.*

# The confidence image 

The confidence image is accessible as part of the data streamed from the O3R device. This image contains information about the validity of each pixel. If a pixel is invalid, the confidence image explains why is has been marked as invalid. The values are as follows:

- 1: CONF_INVALID - indicated that the pixel is invalid;
- 2: CONF_SATURATED - the pixel is overexposed/saturated;
- 4: CONF_BADAMBSYM - the pixel had bad symmetry, probably because of motion;
- 8: CONF_LOWAMP - amplitude lower than the minimum amplitude, or distance noise threshold exceeded;
- (16|32): CONF_EXPINDEX - indicates whether the short, medium of long exposure is used for this pixel;
- 4: CONF_EXPSHIFT - expIndex = (v & CONF_EXPINDEX) >> CONF_EXPSHIFT indicates the index of the exposure time used by this pixel where low indices indicate shorter exposures;                       
- 64: CONF_INVALID_RANGE - the pixel is outside of the measurement range;
- 128: CONF_SUSPECT_PIXEL - this is a bad pixel on the chip;
- 256: RESERVED
- 512: CONF_EDGEPIXEL - edge pixels refer to the image edges which are sometimes invalidated by lateral filters;
- 1024: CONF_UNPLAUSIBLE - pixels remaining after shifting the offset, between the camera and the beginning of the shifted range;
- 2048: CONF_REFLECTIVITY - the reflectivity is below the threshold;
- 4096: CONF_DYNAMIC_AMPLITUDE - the pixel is probably part of the halo around a very bright object;
- 16384: CONF_MIXEDPIXEL - the pixel is a mixed pixel, part of which is measuring the object and the other part the background;
- 32768: CONF_ISOLATED - an isolated pixel with random amplitude in an area where no amplitude is measured.

This look-up table is a result of a more general definition, which has been mostly carried over from previous ifm time-of-flight cameras. These cameras use the PCIC interface communiaction definition as follows:  

The following bits shall be used for all imagers:  
| Bit mask	| Meaning
| --------- | ------------------------
| 0x01	    | != 0 -> pixel is invalid
| 0x02	    | != 0 -> pixel is saturated
| 0x04	    | != 0 -> pixel symmetry criterium not fulfilled
| 0x08	    | != 0 -> pixel invalidated due to an amplitude criterium
| 0x30	    | ((v & 0x30) >> 4) gives the exposure index (this is a change from O3D). 
Exposure index=0 maps to the shortest exposure used in the mode. The maximum value is dependent on the mode. Single exposure modes have a maximum value of 0, double exposure modes gave a maximum value of 1, etc.  
Other bits can be defined by the specific algorithm.
