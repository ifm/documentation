#############################################
# Copyright 2023-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################
# %%
import time
import numpy as np
from ifm3dpy.device import O3R
from ifm3dpy.framegrabber import FrameGrabber, buffer_id

# Edit for the IP address of your OVP8xx and the camera port
IP = "192.168.0.69"
CAMERA_PORT = "port2"
o3r = O3R(IP)

# Ensure a clean slate before running the example
try:
    o3r.reset("/applications/instances")
except Exception as e:
    print(f"Reset failed: {e}")

# Set the extrinsic calibration of the camera
c = {"transX": 0.0, "transY": 0, "transZ": 0.0, "rotX": -1.57, "rotY": 1.57, "rotZ": 0}
print(f"Setting extrinsic calibration for {CAMERA_PORT}")
o3r.set({"ports": {CAMERA_PORT: {"processing": {"extrinsicHeadToUser": c}}}})

# Create the PDS application and
# choose the camera port
print(f"Creating a PDS instance with camera in {CAMERA_PORT}")
o3r.set(
    {"applications": {"instances": {"app0": {"class": "pds", "ports": [CAMERA_PORT]}}}}
)

# Set the application to IDLE (ready to be triggered)
print("Setting the PDS application to IDLE")
o3r.set({"applications": {"instances": {"app0": {"state": "IDLE"}}}})

time.sleep(0.5)
# %%
fg = FrameGrabber(o3r, 51010)


# Define a callback to be executed when a frame is received
def flags_callback(frame):
    """Callback to be executed for each received pallet frame.
    Retrieve the data from the corresponding buffer and
    deserialize it into a JSON array.
    :param frame: the result of the getPallet command.
    """
    if frame.has_buffer(buffer_id(1003)):
        flag_chunk = frame.get_buffer(buffer_id(1003))
        flag_array = np.frombuffer(flag_chunk[0], dtype=np.uint16)
        flag_array = np.reshape(flag_array, (172, 224))
        print(f"Pixel flags: {flag_array}")


PCIC_FORMAT = {
    "layouter": "flexible",
    "format": {"dataencoding": "ascii"},
    "elements": [
        {"type": "string", "value": "star", "id": "start_string"},
        {"type": "blob", "id": "O3R_RESULT_JSON"},
        {"type": "blob", "id": "O3R_RESULT_ARRAY2D"},
        {"type": "string", "value": "stop", "id": "end_string"},
    ],
}
fg.start([1003], pcic_format=PCIC_FORMAT)
fg.on_new_frame(flags_callback)

GET_PALLET_PARAMETERS = {
    "depthHint": -1,
    "palletIndex": 0,  # Block Pallet/EPAL pallet
    "palletOrder": "scoreDescending",
}

# %%
print("Triggering the getPallet command")
o3r.set(
    {
        "applications": {
            "instances": {
                "app0": {
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
