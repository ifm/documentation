###########################################
# 2024-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
###########################################
"""
Setup:  * O3R222 with 3D on port2
            * orientation: camera horizontal (label up, FAKRA cable to the left)
        * getPallet: Pallet(s) in FoV @ over 2.0 m distance
"""
import json
import time
import logging
import numpy as np
from ifm3dpy.device import O3R, Error
from ifm3dpy.framegrabber import FrameGrabber, buffer_id

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Edit for the IP address of your OVP8xx and the camera port and extrinsic calibration
IP = "192.168.0.69"
CAMERA_PORT = "port2"
APP_PORT = "app0"
o3r = O3R(IP)

############################################
# Setup the application
############################################
# Ensure a clean slate before running the example
try:
    o3r.reset("/applications/instances")
except Error as e:
    logger.info(f"Reset failed: {e}")
# Set the extrinsic calibration of the camera
calibration = {
    "transX": 0.0,
    "transY": 0.0,
    "transZ": 0.69,
    "rotX": 0.0,
    "rotY": 1.8,
    "rotZ": 1.57,
}

logger.info(f"Setting extrinsic calibration for {CAMERA_PORT}")
o3r.set({"ports": {CAMERA_PORT: {"processing": {"extrinsicHeadToUser": calibration}}}})

# Creating a PDS instance and setting state to conf to be able to change protected parameters
logger.info(f"Creating a PDS instance with camera in {CAMERA_PORT}")
o3r.set(
    {
        "applications": {
            "instances": {
                APP_PORT: {"class": "pds", "ports": [CAMERA_PORT], "state": "CONF"}
            }
        }
    }
)


# %%
############################################
# Setup the framegrabber to receive frames
# when the application is triggered.
############################################
fg = FrameGrabber(o3r, o3r.port(APP_PORT).pcic_port)
fg.start([buffer_id.O3R_RESULT_JSON])


# Define a callback to be executed when a frame is received
def pallet_callback(frame):
    """Callback to be executed for each received pallet frame.
    Retrieve the data from the corresponding buffer and
    deserialize it into a JSON array.
    :param frame: the result of the getPallet command.
    """
    if frame.has_buffer(buffer_id.O3R_RESULT_JSON):
        json_chunk = frame.get_buffer(buffer_id.O3R_RESULT_JSON)
        json_array = np.frombuffer(json_chunk[0], dtype=np.uint8)
        json_array = json_array.tobytes()
        parsed_json_array = json.loads(json_array.decode())
        logger.info(f"Detected pallet(s): {parsed_json_array['getPallet']['pallet']}")


fg.on_new_frame(pallet_callback)
############################################
# Change the Projection VOI and the minimum
# pixel to validate the pallet
############################################

# Projection Volume shift
y_shift = 0.1
z_shift = 0.1

# Configure the 'getPallet' protected parameters only in CONF state
GET_PALLET_PROTECTED_PARAMETERS = {
    "orthoProjection": {
        "voi": {
            "yMin": -0.8 + y_shift,
            "yMax": 0.8 + y_shift,
            "zMin": -0.4 + z_shift,
            "zMax": 0.4 + z_shift,
        }
    },
    "localizePallets": {
        "faceMinPts": 200, #default is 300
        "stringerMinPts": 50, #default is 70
    }
}


# Setting the protected parameters
logger.info(f"Creating a PDS instance with camera in {CAMERA_PORT} and setting the changed protected parameters")
o3r.set(
    {
        "applications": {
            "instances": {
                APP_PORT: {
                    "class": "pds",
                    "state": "CONF",
                    "ports": [CAMERA_PORT],
                    "configuration": {
                        "parameter": {"getPallet": {"0": GET_PALLET_PROTECTED_PARAMETERS}}
                    },
                }
            }
        }
    }
)
# setting the PDS back to the IDLE state.
o3r.set(
    {
        "applications": {
            "instances": {
                APP_PORT: {"class": "pds", "ports": [CAMERA_PORT], "state": "IDLE"}
            }
        }
    }
)

# Provide the estimated distance to the pallet and the pallet type.
GET_PALLET_PARAMETERS = {
    "depthHint": 2,  # We recommend providing a depth hint for faster detections
    "palletIndex": 0,  # Block Pallet/EPAL pallet
}
# %%
logger.info("Triggering the getPallet command")
o3r.set(
    {
        "applications": {
            "instances": {
                APP_PORT: {
                    "configuration": {
                        "customization": {
                            "command": "getPallet",
                            "getPallet": GET_PALLET_PARAMETERS,
                        }
                    }
                }
            }
        }
    }
)
# Sleep to ensure we have time to execute the callback before exiting.
time.sleep(3)

# %%
fg.stop()
