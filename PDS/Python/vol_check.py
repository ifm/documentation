###########################################
###2023-present ifm electronic, gmbh
###SPDX-License-Identifier: Apache-2.0
###########################################
"""
Setup:  * Camera: O3R222, 3D on port2 
            * orientation: camera horizontally (Fakra cable to the left)
"""
import json
import time
import numpy as np

from ifm3dpy.device import O3R
from ifm3dpy.framegrabber import FrameGrabber, buffer_id

# Device specific configuration
IP = "192.168.0.69"
CAMERA_PORT = "port2"

o3r = O3R(IP)
try:
    o3r.reset("/applications/instances")
except Exception as e:
    print(f"Reset failed: {e}")

c = {"transX": 0.0, "transY": 0, "transZ": 0.0, "rotX": -1.57, "rotY": 1.57, "rotZ": 0}
print(f"Setting the calibration for camera in {CAMERA_PORT}")
o3r.set({"ports": {CAMERA_PORT: {"processing": {"extrinsicHeadToUser": c}}}})

print(f"Create a PDS instance using the camera in {CAMERA_PORT}")
o3r.set(
    {"applications": {"instances": {"app0": {"class": "pds", "ports": [CAMERA_PORT]}}}}
)

print("Set the PDS application state to IDLE")
o3r.set({"applications": {"instances": {"app0": {"state": "IDLE"}}}})

time.sleep(0.5)

fg = FrameGrabber(o3r, 51010)

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
fg.start([1002], pcic_format=PCIC_FORMAT)


def volume_callback(frame):
    """Callback method called every time a frame is received.
    Deserialize the data from the result of the volCheck command.

    :param frame: frame containing the results of the volCheck command
    """
    if frame.has_buffer(buffer_id(1002)):
        json_chunk = frame.get_buffer(buffer_id(1002))
        json_array = np.frombuffer(json_chunk[0], dtype=np.uint8)
        json_array = json_array.tobytes()
        parsed_json_array = json.loads(json_array.decode())
        print(parsed_json_array["volCheck"]["numPixels"])


fg.on_new_frame(volume_callback)

VOLCHECK_PARAMETERS = {
    "xMin": 2,
    "xMax": 3.5,
    "yMin": -0.5,
    "yMax": 0.5,
    "zMin": -0.8,
    "zMax": 0.4,
}

o3r.set(
    {
        "applications": {
            "instances": {
                "app0": {
                    "configuration": {
                        "customization": {
                            "command": "volCheck",
                            "volCheck": VOLCHECK_PARAMETERS,
                        }
                    }
                }
            }
        }
    }
)

time.sleep(3)
fg.stop()
