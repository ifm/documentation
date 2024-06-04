###########################################
###2023-present ifm electronic, gmbh
###SPDX-License-Identifier: Apache-2.0
###########################################

"""
Setup:  * Camera: O3R222, 3D on port2
            * orientation: camera horizontally (FAKRA cable to the left)
        * Item: item in FoV @ 1.5m distance
"""
import json
import time
import numpy as np

from ifm3dpy.device import O3R
from ifm3dpy.framegrabber import FrameGrabber, buffer_id

# Device specific configuration
IP = "192.168.0.69"
CAMERA_PORT = "port2"
APP_PORT = "app0"

GET_ITEM_PARAMETERS = {
    "depthHint": -1,
    "itemIndex": 0,
    "itemOrder": "scoreDescending",
}
TIMEOUT = 6000

o3r = O3R(IP)

try:
    o3r.reset("/applications/instances")
except Exception as e:
    print(f"Reset failed: {e}")

# 1. Set the correct extrinsic calibration
c = {"transX": 0.0, "transY": 0, "transZ": 0.0, "rotX": -1.57, "rotY": 1.57, "rotZ": 0}
print(f"Setting the extrinsic calibration for camera in {CAMERA_PORT}")
o3r.set({"ports": {CAMERA_PORT: {"processing": {"extrinsicHeadToUser": c}}}})

# 2. Create the application instance
print(f"Create a PDS instance using camera in {CAMERA_PORT}")
o3r.set(
    {"applications": {"instances": {APP_PORT: {"class": "pds", "ports": [CAMERA_PORT]}}}}
)

# 3. Set app state to "IDLE" - this is equal to the trigger mode required for the PDS app
print("Set the PDS application to IDLE")
o3r.set({"applications": {"instances": {APP_PORT: {"state": "IDLE"}}}})

# 4. Create the Framegrabber instance and start listening on the socket
fg = FrameGrabber(o3r, o3r.port(APP_PORT).pcic_port)
fg.start([buffer_id.O3R_RESULT_JSON])


# Define a callback function to be executed every time a frame is received
def item_callback(frame):
    """Callback function executed every time a frame is received.
    The data is decoded and the result printed.

    :param frame: A frame containing the data for all the buffer ids
    requested in the start function of the framegrabber.
    """
    if frame.has_buffer(buffer_id.O3R_RESULT_JSON):
        json_chunk = frame.get_buffer(buffer_id.O3R_RESULT_JSON)
        json_array = np.frombuffer(json_chunk[0], dtype=np.uint8)
        json_array = json_array.tobytes()
        parsed_json_array = json.loads(json_array.decode())
        print(parsed_json_array["getItem"]["item"])


fg.on_new_frame(item_callback)

# 5. Call a getItem command: this triggers the image acquisition and pose detection algorithm
o3r.set(
    {
        "applications": {
            "instances": {
                APP_PORT: {
                    "configuration": {
                        "customization": {
                            "command": "getItem",
                            "getItem": GET_ITEM_PARAMETERS,
                        }
                    }
                }
            }
        }
    }
)

# Allow time for the callback to execute before exiting
time.sleep(3)
fg.stop()
