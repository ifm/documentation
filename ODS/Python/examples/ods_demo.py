#%%###################################################################
# Showcases a typical sequence of an ODS application running
# from the initial configuration to the "while true" streaming of data
######################################################################

# Imports
import json
import logging 
from ifm3dpy.device import O3R
from bootup_monitor import BootUpMonitor
from diagnostic import O3RDiagnostic
from ods_config import ODSConfig
from ods_stream import ODSStream

# Initialization of basic objects
ADDR = "192.168.0.69"
o3r = O3R(ADDR)
logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

#%%######################################
# Make sure boot up sequence is completed
#########################################
with BootUpMonitor(o3r) as bootup_monitor:
    try: 
        bootup_monitor.monitor_VPU_bootup()
    except TimeoutError as err:
        raise err

#%%######################################
# Check the diagnostic for any critical errors
#########################################
diag = O3RDiagnostic(o3r=o3r, log_to_file=False)
for err in diag.get_diagnostic_filtered({"state":"active"})["events"]:
    logger.error(f"Active error: {err['id']}, {err['name']}")
logger.info("Review any active errors before continuing.")

#%%######################################
# Start the async diag
#########################################
diag.start_async_diag()

#%%######################################
# Configure two ODS applications (forward and back)
#########################################
o3r.reset("/applications")
ods_config=ODSConfig(o3r=o3r)
# To ensure readability, we first set the extrinsic calibration of
# the cameras and then configure the two ODS instances.
# These two steps can be merged if desired.
ods_config.set_config_from_file("configs/extrinsic_two_heads.json")
ods_config.set_config_from_file("configs/ods_two_apps_config.json")
for app in (apps := ods_config.get(["/applications/instances"])["applications"]["instances"]):
    logger.info(f"Instantiated app: {app}")
# Setting the first app to RUN
ods_config.set_config_from_dict({"applications":{"instances":{list(apps.keys())[0]:{"state":"RUN"}}}})

#%%######################################
# Start streaming data from forward app
#########################################
ods_stream_front = ODSStream(o3r=o3r, app_name=list(apps.keys())[0])
ods_stream_front.start_ods_stream()

#%%######################################
# Display data
#########################################
from ods_viewer import OCVWindow

viewer = OCVWindow("Occupancy grid, zones and diagnostic")#ods_stream_front.get_occupancy_grid().image)
viewer.create_window()
try:
    while True:
        text = "View: front," + "\nZones: " + str(ods_stream_front.get_zones().zone_occupied) + "\nDiagnostic: " + json.dumps(json.loads(diag.diagnostic["message"])["events"][0]["name"])
        viewer.update_image(ods_stream_front.get_occupancy_grid().image, text)
except KeyboardInterrupt:
    logger.info("Vieweing interrupted, turning off data streams. Continuing on with the demo.")

#%%######################################
# Switch to backward app   
#########################################
ods_stream_front.stop_ods_stream()
ods_config.set_config_from_dict({"applications":{"instances":{list(apps.keys())[0]:{"state":"CONF"}}}})
ods_config.set_config_from_dict({"applications":{"instances":{list(apps.keys())[1]:{"state":"RUN"}}}})

ods_stream_back = ODSStream(o3r=o3r, app_name=list(apps.keys())[1])
ods_stream_back.start_ods_stream()

#%%######################################
# Display data
#########################################
try:
    while True:
        text = "View: front," + "\nZones: " + str(ods_stream_back.get_zones().zone_occupied) + "\nDiagnostic: " + json.dumps(json.loads(diag.diagnostic["message"])["events"][0]["name"])
        viewer.update_image(ods_stream_back.get_occupancy_grid().image, text=text)
except KeyboardInterrupt:
    # Turning data streams off and app to CONF to avoid overheating.
    ods_stream_back.stop_ods_stream()
    ods_config.set_config_from_dict({"applications":{"instances":{list(apps.keys())[1]:{"state":"CONF"}}}})
    logger.info("Vieweing interrupted, turning off data streams. End of the demo.")