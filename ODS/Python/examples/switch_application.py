#############################################
# Copyright 2023-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################

# %%

import json
import time
import logging
import numpy as np
from copy import deepcopy

from ifm3dpy import O3R, FrameGrabber
from ifm3dpy import buffer_id

import default_values as default_values
from helper import delete_apps
from ods_examples.bootup_monitor import monitor_bootup
from ods_parse_chunk import Parse_ODS_occupancy_grid

logger = logging.getLogger(__name__)
logging.getLogger("matplotlib").setLevel(logging.ERROR)


def set_dummy_extrinsics(o3r: O3R, port_number: int):
    extrinics = o3r.get([f"/ports/port{port_number}/processing/extrinsicHeadToUser"])
    for i in extrinics["ports"][f"port{port_number}"]["processing"][
        "extrinsicHeadToUser"
    ]:
        extrinics["ports"][f"port{port_number}"]["processing"]["extrinsicHeadToUser"][
            i
        ] = 1
    o3r.set(extrinics)


class AppHandler:
    def __init__(self, o3r: O3R, ip: str, app_active: str, apps: list()) -> None:
        self.ip = ip
        self.o3r = o3r
        self.apps = apps
        self.app_active = app_active
        self.ods_config = dict()

    def set_ods_config(self, ods_config_req):
        # TODO monitor diagnosis information while configuring applications

        self.cam_ports = self.get_cam_ports(ods_config=ods_config_req)
        self._ports_available()
        logger.debug("all requested ports for configuration are available")

        # sequential ods set per app
        try:
            self.o3r.set(ods_config_req)
        except Exception as e:
            logger.error(e)

        app_keys_req = list(ods_config_req["applications"]["instances"].keys())
        app_keys_actual = list(
            self.o3r.get(["/applications/instances"])["applications"][
                "instances"
            ].keys()
        )
        for app_key in app_keys_req:
            if app_key not in app_keys_actual:
                logger.debug("setting applications failed")
                raise RuntimeError("setting applications failed")

        logger.debug("ODS configuration successful")
        self.ods_config = self.o3r.get(["/applications"])

    def get_cam_ports(self, ods_config) -> list:
        cam_ports = []
        for a in ods_config["applications"]["instances"].keys():
            for p in ods_config["applications"]["instances"][a]["ports"]:
                if int(p.split("port")[-1]) in range(0, 6):  # camera ports are [0..5]
                    logger.debug(f"cam port in config: {p}")
                    cam_ports.append(p)
        return cam_ports

    def _ports_available(self) -> None:
        try:
            for cp in self.cam_ports:
                self.o3r.get([f"/ports/{cp}"])
        except Exception as e:
            logger.debug(f"Cam port {cp} failed")
            raise RuntimeError(f"Requested list of ports not available: missing {cp}")

    def _set_app_state(self, app: str, state: str) -> None:
        app0 = self.o3r.get([f"/applications/instances/{app}"])
        app0["applications"]["instances"][app]["state"] = state
        self.o3r.set(app0)
        assert self._check_app_state(app=app, state=state)

    def _check_app_state(self, app: str, state: str) -> bool:
        app0 = self.o3r.get([f"/applications/instances/{app}"])
        return app0["applications"]["instances"][app]["state"] == state

    def set_app_active(self, app_req: str) -> None:
        if app_req not in self.apps:
            raise ValueError("app not available")

        # set currently active app to CONF state if not equal to requested app
        if self.app_active != "" and app_req != self.app_active:
            self._set_app_state(app=self.app_active, state="CONF")
        self._set_app_state(app=app_req, state="RUN")
        self.app_active = app_req

        # additional grace period to allow the ODS applications vo module to fully initialize
        time.sleep(5)

    def set_all_apps_inactive(self) -> None:
        for app in self.apps:
            self._set_app_state(app=app, state="CONF")

    def get_data(self, app: str) -> bool:
        if app != self.app_active:
            raise RuntimeError("No active app")

        # get the applications TCP port
        pcicTCPPort = self.o3r.get([f"/applications/instances/{app}/data/pcicTCPPort"])[
            "applications"
        ]["instances"][app]["data"]["pcicTCPPort"]

        fg = FrameGrabber(self.o3r, pcicTCPPort)
        fg.start([buffer_id.O3R_ODS_OCCUPANCY_GRID, buffer_id.O3R_ODS_INFO])

        time.sleep(0.5)  # grace period

        # TODO monitor diagnosis information while retrieving data
        for c in range(10):
            [ok, frame] = fg.wait_for_frame().wait_for(1000)

            if frame is not None:
                logger.debug(f"image acquisition successful after {c} sec")

                assert frame.has_buffer(buffer_id.O3R_ODS_OCCUPANCY_GRID)
                assert frame.has_buffer(buffer_id.O3R_ODS_INFO)

                occ_grid = np.array(frame.get_buffer(buffer_id.O3R_ODS_OCCUPANCY_GRID))
                parse_ods_data = Parse_ODS_occupancy_grid(occ_grid)
                occupancy_grid_image = parse_ods_data.occupancy_grid

                num_non_zero = np.count_nonzero(occupancy_grid_image > 0)
                assert num_non_zero > 0

                logger.debug(f"number of valid pixels in occ grid: {num_non_zero}")
                logger.info("successful app switch")
                return True

        return False


def get_single_app_instances(ods_config: dict) -> list:
    single_app_instances = []
    all_ods_apps = list(ods_config["applications"]["instances"].keys())
    for ods_app_req in all_ods_apps:
        other_apps = [x for x in all_ods_apps if x != ods_app_req]
        ods_config_copy = deepcopy(ods_config)
        for op in other_apps:
            del ods_config_copy["applications"]["instances"][op]
        single_app_instances.append(ods_config_copy)

    return single_app_instances


# %%


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    IP = "192.168.0.69"
    o3r = O3R(ip=IP)
    try:
        monitor_bootup(ip=IP, o3r=o3r, stages=["device", "ports", "applications"])
        logger.debug("O3R device available")
    except TimeoutError as e:
        logger.error(
            "no connection to VPU device with camera heads connected could be established"
        )
        raise e

    if delete_apps.check_for_existing_app(o3r):
        delete_apps.delete_existing_app(o3r)
        logger.debug("deleted all existing apps")

    ods_2app_conf = default_values.ODS_APP_SWITCH_CONFIG
    with open(ods_2app_conf) as file:
        ods_config = json.load(file)

    # 1. create am app Handlder object
    apps_list = list(ods_config["applications"]["instances"].keys())
    app_handle = AppHandler(ip=IP, o3r=o3r, app_active="", apps=apps_list)

    # 2. set ODS applications: i.e. create application instances
    single_apps = get_single_app_instances(ods_config)
    for sg in single_apps:
        app_handle.set_ods_config(sg)
    logger.debug(
        f'Applications available after sequential configuration:\n {app_handle.ods_config["applications"]["instances"].keys()}'
    )

    # 3. set extrinsic calibration for ODS application to be functional
    for p in app_handle.get_cam_ports(ods_config):
        set_dummy_extrinsics(app_handle.o3r, port_number=p.split("port")[-1])

    # 4.1. set one app active and request some data
    app_handle.set_app_active(app_req="app0")
    app_handle.get_data(app="app0")

    # 4.2. set a different app active and request some data
    app_handle.set_app_active(app_req="app1")
    app_handle.get_data(app="app1")

    # 5. request data from a non-active app
    try:
        app_handle.get_data(app="app0")
    except RuntimeError as e:
        logger.error(e)

    # 6. set all apps to inactive state, i.e. to save battery power
    app_handle.set_all_apps_inactive()


if __name__ == "__main__":
    main()
# %%
