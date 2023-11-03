###########################################
###2023-present ifm electronic, gmbh
###SPDX-License-Identifier: Apache-2.0
###########################################

"""
Setup:  * O3R222   3D on port2
            * orientation: camera horizontally (FAKRA cable to the left)
        * getItem: item/s in FoV @ 1.5m distance
"""
import ifm3dpy
from ifm3dpy.device import Error as ifm3dpy_error
import json
from ifm3dpy.framegrabber import FrameGrabber, buffer_id
import numpy as np

# MAGIC NUMBERS
APP_PCIC_PORT = 51010
PCIC_FORMAT = {
  "layouter": "flexible",
  "format": {
    "dataencoding": "ascii"
  },
  "elements": [
    {
      "type": "string",
      "value": "star",
      "id": "start_string"
    },
    {
      "type": "blob",
      "id": "O3R_RESULT_JSON"
    },
    {
      "type": "blob",
      "id": "O3R_RESULT_ARRAY2D"
    },
    {
      "type": "string",
      "value": "stop",
      "id": "end_string"
    }
  ]
}
GET_ITEM_PARAMETERS = {
          "depthHint": -1,
          "itemIndex": 0,
          "palletOrder": "scoreDescending"
        }
TIMEOUT = 6000
BUFFER_ID_PDS_JSON = 1002
BUFFER_ID_PDS_IMG = 1003


o3r = ifm3dpy.O3R()
try:
    o3r.reset("/applications/instances")
except Exception as e:
    print("Reset failed: %s" % (e))
    pass

# 1. Set the correct extrinsic calibration
c = dict(transX=0.0, transY=0, transZ=0.0, rotX=-1.57, rotY=1.57, rotZ=0)
print("set(/ports/port2/processing/extrinsicHeadToUser)")
o3r.set({"ports": {"port2": {"processing":{"extrinsicHeadToUser": c}}}})

# 2. Create the application instance
print("set(/applications/instances/app0/class:pds, ports:port2)")
o3r.set({"applications": {"instances": {"app0": {"class": "pds", "ports": ["port2"]}}}})

# 3. Set app state to "IDLE" - this is equal to the trigger mode required for the PDS app
print("set(/applications/instances/app0/state:IDLE)")
o3r.set({"applications": {"instances": {"app0": {"state": "IDLE"}}}})

# 4. Create the Framegrabber instance and start listening on the socket
print("create framegrabber instance")
fg = FrameGrabber(o3r,APP_PCIC_PORT)
fg.start([BUFFER_ID_PDS_JSON, BUFFER_ID_PDS_IMG], pcic_format=PCIC_FORMAT)
print("Init done")


# 5. Call a getItem command: this triggers the image acquisition and pose detection algorithm
o3r.set({"applications": {"instances": {"app0": {"configuration": {"customization":{"command": "getItem", "getItem":GET_ITEM_PARAMETERS }}}}}})

[ok, frame] = fg.wait_for_frame().wait_for(TIMEOUT)

if ok:
    if frame.has_buffer(buffer_id(BUFFER_ID_PDS_JSON)):
            json_chunk = frame.get_buffer(buffer_id(BUFFER_ID_PDS_JSON))
            json_array = np.frombuffer(json_chunk[0], dtype=np.uint8)
            json_array = json_array.tobytes()
            parsed_json_array = json.loads(json_array.decode())
            print(parsed_json_array["getItem"]["item"])
else:
     raise RuntimeError("Failed to grab images: verify the connectivity and application instance")