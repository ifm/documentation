#%%
from ifm3dpy import O3R, FrameGrabber, buffer_id
from ifm3dpy.deserialize import ODSInfoV1, ODSOccupancyGridV1

#%%
from os import getenv

IP = getenv("IFM3D_IP", "192.168.0.69")
o3r = O3R(IP)
fg = FrameGrabber(o3r, 51010)
SCHEMA = {
    "layouter": "flexible",
    "format": {"dataencoding": "ascii"},
    "elements": [
        {"type": "string", "value": "star", "id": "start_string"},
        {"type": "blob", "id": "O3R_ODS_OCCUPANCY_GRID"},
        {"type": "blob", "id": "O3R_ODS_INFO"},
        {"type": "string", "value": "stop", "id": "end_string"},
    ],
}
fg.start([buffer_id.O3R_ODS_OCCUPANCY_GRID, buffer_id.O3R_ODS_INFO], SCHEMA)
#%%
[ok, frame] = fg.wait_for_frame().wait_for(1000)

# %%
ods_info = ODSInfoV1.deserialize(frame.get_buffer(buffer_id.O3R_ODS_INFO))

# %%
