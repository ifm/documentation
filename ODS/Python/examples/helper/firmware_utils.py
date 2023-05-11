#############################################
# Copyright 2023-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################

import argparse
import time
import logging
from time import sleep
import json
import os
from pathlib import Path

from ifm3dpy.device import O3R
from ifm3dpy.swupdater import SWUpdater

# from helper.bootup_monitor import monitor_bootup
from ods_examples.bootup_monitor import BootUpMonitor

logger = logging.getLogger(__name__)


def _update_firmware_via_recovery(o3r: O3R, filename: str) -> None:
    logger.debug(f"Start FW update with file: {filename}")

    sw_updater = SWUpdater(o3r)
    sw_updater.reboot_to_recovery()
    sleep(2)  # allow grace period before requesting recovery state

    logger.debug("Requesting reboot to recovery")

    if not sw_updater.wait_for_recovery(60000):
        raise RuntimeError("Device failed to boot into recovery")

    if not sw_updater.flash_firmware(filename, timeout_millis=120000):
        _reboot_productive(o3r=o3r)
        raise RuntimeError("Firmware update failed")

    logger.debug("Flashing FW via recovery successful")
    logger.debug("Requesting final reboot after FW update")
    sleep(2)  # allow grace period before reboot after update


def _reboot_productive(o3r: O3R) -> None:
    sw_updater = SWUpdater(o3r)
    logger.info("wait for productive system")
    sw_updater.wait_for_productive(20000)

    logger.info("reboot to productive system")
    sw_updater.reboot_to_productive()


def _check_ifm3dpy_version_12x():
    import ifm3dpy

    version = ifm3dpy.__version__
    logger.info(f"ifm3dpy version: {version}")

    major, minor, patch = version.split(".")
    if (int(major), int(minor), int(patch)) >= (1, 2, 1):
        return True


#%%
def update_fw(filename):
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    if not _check_ifm3dpy_version_12x():
        raise RuntimeError(
            "ifm3dpy version not compatible. \nUpgrade via pip install -U ifm3dpy"
        )
        # pip uninstall -y ifm3dpy &&  pip install -i https://test.pypi.org/simple/ ifm3dpy

    IP = os.environ.get("IFM3D_IP", "192.168.0.69")
    logger.info(f"device IP: {IP}")

    logger.info(f"FW swu file: {filename}")

    o3r = O3R(IP)

    config_back_fp = Path("config_backup.json")
    with open(config_back_fp, "w", encoding="utf-8") as f:
        json.dump(o3r.get(), f, ensure_ascii=False, indent=4)
        logger.info(f"current config dumped to: {Path.absolute(config_back_fp)}")

    # update firmware
    logger.info("start FW update process")
    _update_firmware_via_recovery(o3r, filename)
    logger.info("Update process: file transfer completed")

    _reboot_productive(o3r)
    logger.info("Reboot to productive system completed")

    # wait for system ready
    with BootUpMonitor(
        o3r, stages=["device", "ports", "applications"], timeout=60, wait_time=1
    ) as boot_up:
        try:
            boot_up.monitor_VPU_bootup()

        except TimeoutError as e:
            logger.error(e)
            raise e

    logger.debug("Firmware update complete: device available again")

    # check firmware version after update
    time.sleep(
        10
    )  # grace period after initial bootup before software version can be queried
    major, minor, patch = get_firmware_version(o3r)
    logging.info(f"Firmware version after update: {(major, minor, patch)}")

    # reapply configuration after update
    with open(config_back_fp, "r") as f:
        try:
            o3r.set(json.load(f))
        except Exception as e:
            logger.error(f"failed to apply prev config: {e}")
            schema_fp = Path("json_schema.json")
            with open(schema_fp, "w", encoding="utf-8") as f:
                json.dump(o3r.get_schema(), f, ensure_ascii=False, indent=4)
                logger.info(
                    f"current json schema dumped to: {Path.absolute(schema_fp)}"
                )

            logger.warning(
                f"check config against json schema: \n{Path.absolute(schema_fp)}"
            )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Firmware update helper", description="Update the O3R embedded firmware"
    )
    parser.add_argument("filename", help="SWU filename in the cwd")
    args = parser.parse_args()

    update_fw(filename=args.filename)
#%%
