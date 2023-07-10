#############################################
# Copyright 2023-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################

# %%
import argparse
import time
import logging
from time import sleep
import json
import os
from pathlib import Path

from ifm3dpy.device import O3R
from ifm3dpy.device import Error as ifm3dpy_error
from ifm3dpy.swupdater import SWUpdater

from bootup_monitor import BootUpMonitor

logger = logging.getLogger(__name__)
TIMEOUT = 60
TIMEOUT_MILLIS = 300000


def _get_firmware_version(o3r: O3R) -> tuple:
    try:
        firmware = o3r.get(["/device/swVersion/firmware"])["device"]["swVersion"][
            "firmware"
        ]
    except Exception as e:
        logger.error(e)
        raise e
    logger.debug(f"VPU firmware: {firmware}")
    try:
        major, minor, patch = firmware.split(".")
        patch = patch.split("-")[0]
        return (major, minor, patch)
    except ValueError as e:
        return None


def _update_firmware_016_to_10x(o3r: O3R, filename: str) -> None:
    logger.info(f"Start FW update with file: {filename}")
    sw_updater = SWUpdater(o3r)

    # 1st application of FW update
    logger.debug("First flash FW file")
    sw_updater.flash_firmware(filename, timeout_millis=TIMEOUT_MILLIS)

    # grace period reboot
    logger.debug("Sleep 10 sec grace period before reboot")
    time.sleep(10)

    logger.debug("Monitor recovery mode after initial flash")
    if not sw_updater.wait_for_recovery(120000):  # Change 60000 to 120000
        raise RuntimeError("Device failed to boot into recovery in 2 minutes")

    logger.debug("Boot to recovery mode successful")

    # 2nd application of FW update: final flash
    logger.debug("Second flash FW file")
    if not sw_updater.flash_firmware(filename, timeout_millis=TIMEOUT_MILLIS):
        _reboot_productive(o3r=o3r)
        raise RuntimeError("Firmware update failed")

    logger.debug("Request reboot to productive after second FW flash")
    logger.debug("Second FW flash successful")


def _update_firmware_via_recovery(o3r: O3R, filename: str) -> None:
    logger.debug(f"Start FW update with file: {filename}")

    sw_updater = SWUpdater(o3r)
    logger.debug("Rebooting the device to recovery mode")
    sw_updater.reboot_to_recovery()
    sleep(2)  # allow grace period before requesting recovery state

    if not sw_updater.wait_for_recovery(120000):  # Change 60000 to 120000
        raise RuntimeError("Device failed to boot into recovery in 2 minutes")

    logger.debug("Boot to recovery mode successful")
    if not sw_updater.flash_firmware(filename, timeout_millis=TIMEOUT_MILLIS):
        logger.debug("Firmware update failed. Boot to productive mode")
        _reboot_productive(o3r=o3r)
        logger.debug("Reboot to productive system completed")
        raise RuntimeError

    logger.debug("Flashing FW via recovery successful")
    logger.debug("Requesting final reboot after FW update")
    sleep(2)  # allow grace period before reboot after update

    _reboot_productive(o3r)
    logger.info("Reboot to productive system completed")


def _reboot_productive(o3r: O3R) -> None:
    sw_updater = SWUpdater(o3r)
    logger.info("reboot to productive system")
    sw_updater.reboot_to_productive()
    logger.info("Allow grace period of 60 seconds to reboot to productive system")
    sleep(60)
    sw_updater.wait_for_productive(120000)


def __check_ifm3dpy_version():
    import ifm3dpy

    version = ifm3dpy.__version__
    logger.info(f"ifm3dpy version: {version}")

    major, minor, patch = version.split(".")
    return (int(major), int(minor), int(patch))


def _check_ifm3dpy_version_12x():
    major, minor, patch = __check_ifm3dpy_version()
    if (int(major), int(minor)) == (1, 2):
        return True


def _check_ifm3dpy_version_13x():
    major, minor, patch = __check_ifm3dpy_version()
    if (int(major), int(minor), int(patch)) >= (1, 3, 3):
        return True


# %%
def update_fw(filename):
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    if not _check_ifm3dpy_version_13x():
        raise RuntimeError(
            "ifm3dpy version not compatible. \nUpgrade via pip install -U ifm3dpy"
        )

    IP = os.environ.get("IFM3D_IP", "192.168.0.69")
    os.environ["IFM3D_SWUPDATE_CURL_TIMEOUT"] = "1000"  # Previously: 800

    logger.info(f"device IP: {IP}")
    logger.info(f"FW swu file: {filename}")
    logger.info(
        f"Monitoring of FW update via messages tab here: http://{IP}:8080/"
    )

    o3r = O3R(IP)

    # check FW 0.16.23
    major, minor, patch = _get_firmware_version(o3r)
    logging.info(f"Firmware version before update: {(major, minor, patch)}")
    if int(major) == 0 and any([int(minor) < 16, int(patch) < 23]):
        logging.error("Update to FW 0.16.23 first before updating to version 1.0.14")
        raise RuntimeError(
            "Update to FW 0.16.23 first before updating to version 1.0.14"
        )

    config_back_fp = Path("config_backup.json")
    with open(config_back_fp, "w", encoding="utf-8") as f:
        json.dump(o3r.get(), f, ensure_ascii=False, indent=4)
        logger.info(f"current config dumped to: {Path.absolute(config_back_fp)}")

    # update firmware
    logger.info("start FW update process")
    if (int(major), int(minor), int(patch)) == (0, 16, 23):
        logger.info("FW Update 0.16.23 to 1.0.x started")
        _update_firmware_016_to_10x(o3r, filename)
        logger.info("Update process: file transfer completed")
    elif (int(major), int(minor)) >= (1, 0):
        logger.info("FW Update via recovery started")
        _update_firmware_via_recovery(o3r, filename)
        logger.info("Update process: file transfer completed")
    else:
        logger.error("This FW update is not supported")

    # wait for system ready
    with BootUpMonitor(o3r, timeout=60, wait_time=1) as boot_up:
        try:
            boot_up.monitor_VPU_bootup()

        except TimeoutError as e:
            logger.error(e)
            raise e

    logger.debug("Firmware update complete: device available again")

    # check firmware version after update
    time.sleep(10)
    # grace period after initial bootup before software version can be queried

    major, minor, patch = _get_firmware_version(o3r)
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
# %%
