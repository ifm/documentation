###########################################
###2023-present ifm electronic, gmbh
###SPDX-License-Identifier: Apache-2.0
###########################################
"""
Setup:  * O3R222   3D on port2 
            * orientation: camera horizontally (Fakra cable to the left)
        * getPallet: pallet with load in FoV @ 1.5m distance
"""
import ifm3dpy
from ifm3dpy.device import Error as ifm3dpy_error
import json
from ifm3dpy.framegrabber import FrameGrabber, buffer_id
import numpy as np
import time
import default_values

o3r = ifm3dpy.O3R()
try:
    o3r.reset("/applications/instances")
except Exception as e:
    print("Reset failed: %s" % (e))
    pass

c = dict(transX=0.0, transY=0, transZ=0.0, rotX=-1.57, rotY=1.57, rotZ=0)
print("set(/ports/port2/processing/extrinsicHeadToUser)")
o3r.set({"ports": {"port2": {"processing":{"extrinsicHeadToUser": c}}}})

print("set(/applications/instances/app0/class:pds, ports:port2)")
o3r.set({"applications": {"instances": {"app0": {"class": "pds", "ports": ["port2"]}}}})

print("set(/applications/instances/app0/state:IDLE)")
o3r.set({"applications": {"instances": {"app0": {"state": "IDLE"}}}})

time.sleep(0.5)

print("create framegrabber instance")
fg = FrameGrabber(o3r,51010)

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
fg.start([1002,1003], pcic_format=PCIC_FORMAT)
print("Init done")

GET_PALLET_PARAMETERS = {
          "depthHint": -1, 
          "palletIndex": 0, # Block Pallet/EPAL pallet
          "palletOrder": "scoreDescending"
        }

o3r.set({"applications": {"instances": {"app0": {"configuration": {"customization":{"command": "getPallet", "getPallet":GET_PALLET_PARAMETERS }}}}}})
[ok, frame] = fg.wait_for_frame().wait_for(6000)

if ok:
    if frame.has_buffer(buffer_id(1003)):
            json_chunk = frame.get_buffer(buffer_id(1002))
            json_array = np.frombuffer(json_chunk[0], dtype=np.uint8)
            json_array = json_array.tobytes()
            parsed_json_array = json.loads(json_array.decode())
            print(parsed_json_array["getPallet"]["pallet"])