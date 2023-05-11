import argparse
import ctypes as ct
import io
import json
import logging
import struct
import sys
from threading import Event, Thread
from xmlrpc.client import ServerProxy

import bottleneck as bn
import numpy as np
from ifm_o3r_algodebug.Receiver import ADReceiver
from ifm_o3r_apc.camtoworld import CamToWorld
# from ifm_o3r_ods import transformations as tr
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from scipy.optimize import least_squares  # , leastsq, OptimizeResult

logger = logging.getLogger(__name__)

plt.rcParams["toolbar"] = "None"  # Disable toolbar

STANDARD_GRAVITY = 9.80665


class AlgoExtrinsicCalibration(ct.Structure):
    _fields_ = [
        ("transX", ct.c_float),
        ("transY", ct.c_float),
        ("transZ", ct.c_float),
        ("rotX", ct.c_float),
        ("rotY", ct.c_float),
        ("rotZ", ct.c_float)
    ]


class EM_IIM42652_Sample(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_int64),
        ("temperature", ct.c_float),
        ("accel_x", ct.c_float),
        ("accel_y", ct.c_float),
        ("accel_z", ct.c_float),
        ("gyro_x", ct.c_float),
        ("gyro_y", ct.c_float),
        ("gyro_z", ct.c_float)
    ]


class EM_IIM42652_IFOutput(ct.Structure):
    _fields_ = [
        ("imuSamples", 128 * EM_IIM42652_Sample),
        ("numSamples", ct.c_uint32),
        ("extrinsicIMUToUser", AlgoExtrinsicCalibration),
        ("gyroNoise", ct.c_float),
        ("accelNoise", ct.c_float)
    ]


class EMSpecificCustomization(ct.Structure):
    _fields_ = [
        ("cutoffFrequency", ct.c_float),
        ("outputFrequency", ct.c_float)
    ]


class EM_IIM42652_Customization(ct.Structure):
    _fields_ = [
        ("emParam", EMSpecificCustomization),
        ("extrinsicVPUToUser", AlgoExtrinsicCalibration)
    ]


def round_floats(o, n):
    if isinstance(o, float):
        return round(o, n)
    if isinstance(o, dict):
        return {k: round_floats(v, n) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [round_floats(x, n) for x in o]
    return o


def generate_text_string(header, tuple_list, footer):
    text_string = header
    for x in tuple_list:
        text_string += "\n"
        text_string += x[0] + " = " + str(round_floats(x[1], 8)) + " " + x[2]
    text_string += "\n"
    text_string += footer
    return text_string


class EMADReceiver:
    def __init__(self, ip, source):
        self.ip = ip
        self.source = source

        self.rcv = None

        self.calib = None
        self.custom = None
        self.ifout = []

    def connect(self):
        self.rcv = ADReceiver(self.ip, self.source, autostart=True)
        self.rcv.connect()

    def get(self, cb_fun=None):
        if self.rcv is None:
            raise RuntimeError("connect() must be called first")
        else:
            packet = self.rcv.get()

            def read_packet(packet, channel):
                packet_size = 0

                def buf_read(size):
                    nonlocal packet_size
                    packet_size += size
                    res = buf.read(size)
                    if len(res) != size:
                        raise EOFError("End of file reached")
                    return res

                buf = io.BytesIO(packet)
                item, = struct.unpack("<I", buf_read(4))
                if item == 0xffffdeda:
                    ok = False
                    while True:
                        item, = struct.unpack("<I", buf_read(4))
                        if item == 0xadedffff:
                            ok = True
                            break
                        if item != 0x01234567:
                            raise RuntimeError("Can't find magic number (channel start)")
                        size, = struct.unpack("<I", buf_read(4))
                        if size == 0 or size > 1024 * 1024 * 1024:
                            raise RuntimeError("Invalid size argument")
                        cid = buf_read(size - 1)
                        cid = cid.decode("utf-8")
                        buf_read(1)
                        item, = struct.unpack("<I", buf_read(4))
                        if item != 0x76543210:
                            raise RuntimeError("Can't find magic number (channel mid)")
                        size, = struct.unpack("<I", buf_read(4))
                        if size == 0 or size > 1024 * 1024 * 1024:
                            raise RuntimeError("Invalid size argument")
                        desc = buf_read(size)
                        item, = struct.unpack("<I", buf_read(4))
                        if item != 0x76543210:
                            raise RuntimeError("Can't find magic number (channel mid)")
                        size, = struct.unpack("<I", buf_read(4))
                        if size == 0 or size > 1024 * 1024 * 1024:
                            raise RuntimeError("Invalid size argument")
                        data = buf_read(size)
                        item, = struct.unpack("<I", buf_read(4))
                        if item != 0x89abcdef:
                            raise RuntimeError("Can't find magic number (channel end)")
                        if channel not in ["em/ifcalib", "em/ifout", "em/ifcustom"]:
                            raise RuntimeError("Unsupported channel %s" % channel)
                        elif cid == channel:
                            if channel == "em/ifcalib":
                                ret = json.loads(data[:-4].decode("utf-8").rstrip("\x00").encode())
                            if channel == "em/ifout":
                                ret = EM_IIM42652_IFOutput()
                                ct.memmove(ct.addressof(ret), data, ct.sizeof(ret))
                            elif channel == "em/ifcustom":
                                ret = EM_IIM42652_Customization()
                                ct.memmove(ct.addressof(ret), data, ct.sizeof(ret))
                            return ret
                    if not ok:
                        raise RuntimeError("Unexpected end of stream")

            if self.calib is None:
                self.calib = read_packet(packet, "em/ifcalib")
            if self.custom is None:
                self.custom = read_packet(packet, "em/ifcustom")

            ifout = read_packet(packet, "em/ifout")
            if ifout is not None:
                if cb_fun is not None:
                    cb_fun(ifout)
                else:
                    self.ifout += [ifout]

    def disconnect(self):
        self.rcv.disconnect()
        self.rcv = None


class VPUExtrinsicCalibrationXMLRPC:
    def __init__(self, ip="192.168.0.69", source="port6", save_init=True, mode="experimental_ods"):
        self.ip = ip
        self.source = source
        self.save_init = save_init
        self.mode = mode

    def __generate_json_dump(self, extrinsic_vpu_user):
        return {
            "ports": {
                self.source: {
                    "mode": self.mode,
                    "processing": {
                        "extrinsicVPUToUser": {
                            "rotX": round_floats(extrinsic_vpu_user.rotX, 8),
                            "rotY": round_floats(extrinsic_vpu_user.rotY, 8),
                            "rotZ": round_floats(extrinsic_vpu_user.rotZ, 8),
                            "transX": round_floats(extrinsic_vpu_user.transX, 8),
                            "transY": round_floats(extrinsic_vpu_user.transY, 8),
                            "transZ": round_floats(extrinsic_vpu_user.transZ, 8)
                        }
                    }
                }
            }
        }

    def __json_configs_equal(self, json_config_set, json_config_get):
        json_configs_close = True
        for attr, _ in AlgoExtrinsicCalibration()._fields_:
            np.logical_and(json_configs_close,
                           np.isclose(
                               json_config_set["ports"][self.source]["processing"]["extrinsicVPUToUser"][attr],
                               json_config_get["ports"][self.source]["processing"]["extrinsicVPUToUser"][attr]))
        return json_configs_close

    def get(self):
        with ServerProxy(f"http://{self.ip}/api/rpc/v1/com.ifm.efector/") as prx:
            json_config = json.loads(prx.get([f"/ports/{self.source}/processing/extrinsicVPUToUser"]))
            logger.debug("get(): {}".format(json_config))
        extrinsic_vpu_user = AlgoExtrinsicCalibration()
        for attr, _ in AlgoExtrinsicCalibration()._fields_:
            if attr in json_config["ports"][self.source]["processing"]["extrinsicVPUToUser"]:
                setattr(extrinsic_vpu_user, attr, json_config["ports"][self.source]["processing"]["extrinsicVPUToUser"][attr])
        return extrinsic_vpu_user

    def set(self, extrinsic_vpu_user):
        json_config_set = self.__generate_json_dump(extrinsic_vpu_user)
        logger.debug("set(): {}".format(json_config_set))
        with ServerProxy(f"http://{self.ip}/api/rpc/v1/com.ifm.efector/") as prx:
            prx.set(json.dumps(json_config_set))
            if self.save_init:
                prx.saveInit()
            json_config_get = json.loads(prx.get([f"/ports/{self.source}/processing/extrinsicVPUToUser"]))
            logger.debug("get(): {}".format(json_config_get))
        return self.__json_configs_equal(json_config_get, json_config_set)


class VPUMisalignmentEstimationGUI:
    def __init__(self, ip, source):
        self.ip = ip
        self.source = source

        try:
            assert self.source == "port6"
            self.rcv = EMADReceiver(self.ip, self.source)
            self.xml_rpc = VPUExtrinsicCalibrationXMLRPC(self.ip, self.source, True, "experimental_ods")
            self.extrinsic_vpu_user = self.xml_rpc.get()
            self.extrinsic_vpu_user_updated = AlgoExtrinsicCalibration()
        except Exception as e:
            logger.error("Unable to connect to VPU (ip: {}, source: {})".format(self.ip, self.source))
            return  # Return immediately

        self.stop_event = Event()
        self.rcv_thread = Thread(target=self.__get_data, daemon=True)

        self.ts_init = 0
        self.ts = []
        self.gyro_x = []
        self.gyro_y = []
        self.gyro_z = []
        self.accel_x = []
        self.accel_y = []
        self.accel_z = []
        self.rot_imu_user = np.eye(3)
        self.rot_vpu_user = CamToWorld.rotMat(self.extrinsic_vpu_user.rotX,
                                              self.extrinsic_vpu_user.rotY,
                                              self.extrinsic_vpu_user.rotZ)
        self.gyro_noise = None
        self.accel_noise = None

        self.fig = None
        self.ax0 = None  # gyro_x (aligned)
        self.ax1 = None  # gyro_y (aligned)
        self.ax2 = None  # gyro_z (aligned)
        self.ax3 = None  # gyro_x (original)
        self.ax4 = None  # gyro_y (original)
        self.ax5 = None  # gyro_z (original)
        self.ln0 = None
        self.ln1 = None
        self.ln2 = None
        self.bt0 = None  # "Start Recording"
        self.bt1 = None  # "Stop Recording"
        self.bt2 = None  # "Estimate Misalignment"
        self.bt3 = None  # "Save to VPU"
        self.bt4 = None  # "Close Window"
        self.cidbt0 = 0
        self.cidbt1 = 0
        self.cidbt2 = 0
        self.cidbt3 = 0
        self.cidbt4 = 0
        self.axtb0 = None  # General information
        self.axtb1 = None  # Information about misalignment estimation
        self.axtb1_invisible = None
        self.axtb2 = None  # Information about extrinsic calibration
        self.axtb3 = None  # Information about instructions
        self.axtb3_invisible = None

        self.samples_to_display = 1000  # 1000 samples corresponds to 10 seconds
        self.anim = None

        self.window_mean = 101

        self.__setup_fig()

    def __setup_fig(self):
        self.fig = plt.figure("VPU Misalignment Estimation", figsize=(16.0, 9.6), dpi=72)
        self.ax0 = plt.subplot(2, 3, 1)
        self.ax0.plot([], [], color="tab:blue", label=r"$\omega_x$")
        self.ax0.legend(loc="upper right")
        self.ax1 = plt.subplot(2, 3, 2, sharey=self.ax0)
        self.ax1.plot([], [], color="tab:blue", label=r"$\omega_y$")
        self.ax1.legend(loc="upper right")
        self.ax2 = plt.subplot(2, 3, 3)
        self.ax2.plot([], [], color="tab:blue", label=r"$\omega_z$")
        self.ax2.legend(loc="upper right")
        self.ax0.set_ylabel(r"$\omega$ [rad/s] (aligned)")
        plt.setp(self.ax0.get_xticklabels(), visible=False)
        plt.setp(self.ax1.get_xticklabels(), visible=False)
        plt.setp(self.ax2.get_xticklabels(), visible=False)
        self.ax3 = plt.subplot(2, 3, 4)
        self.ln0, = self.ax3.plot([], [], color="tab:blue", label=r"$\omega_x$")
        self.ax3.legend(loc="upper right")
        self.ax4 = plt.subplot(2, 3, 5, sharey=self.ax3)
        self.ln1, = self.ax4.plot([], [], color="tab:blue", label=r"$\omega_y$")
        self.ax4.legend(loc="upper right")
        self.ax5 = plt.subplot(2, 3, 6)
        self.ln2, = self.ax5.plot([], [], color="tab:blue", label=r"$\omega_z$")
        self.ax5.legend(loc="upper right")
        self.ax3.set_ylabel(r"$\omega$ [rad/s] (original)")
        self.ax3.set_xlabel("$t$ [s]")
        self.ax4.set_xlabel("$t$ [s]")
        self.ax5.set_xlabel("$t$ [s]")
        self.fig.tight_layout()
        self.fig.subplots_adjust(left=0.075, right=0.8)
        self.axtb0 = plt.axes([0.825, 0.85, 0.15, 0.125])
        self.axtb0.axis("off")
        self.axtb0.text(0.5, 0.5,
                        "Record IMU data while moving vehicle\n" +
                        "on a path shaped like a \"lying eight\",\n" +
                        "i.e., a right turn followed by a left turn,\n" +
                        "to estimate VPU misalignment and\n" +
                        "update extrinsic VPU calibration\n" +
                        "\n" +
                        "Important: Wait for one second before\n" +
                        "moving in positive x-direction first",
                        horizontalalignment="center", verticalalignment="center")
        self.axtb1 = plt.axes([0.825, 0.475, 0.15, 0.1])
        self.axtb1.xaxis.set_visible(False)
        self.axtb1.yaxis.set_visible(False)
        self.axtb1_invisible = plt.axes([0.825, 0.375, 0.15, 0.2])
        self.axtb1_invisible.axis("off")
        self.axtb2 = plt.axes([0.825, 0.3, 0.15, 0.15])
        self.axtb2.xaxis.set_visible(False)
        self.axtb2.yaxis.set_visible(False)
        self.axtb2.text(0.05, 0.95,
                        generate_text_string(
                            "extrinsicVPUToUser (currently\n" +
                            "stored on VPU):",
                            [
                                ("rotX", self.extrinsic_vpu_user.rotX, "rad"),
                                ("rotY", self.extrinsic_vpu_user.rotY, "rad"),
                                ("rotZ", self.extrinsic_vpu_user.rotZ, "rad"),
                                ("transX", self.extrinsic_vpu_user.transX, "m"),
                                ("transY", self.extrinsic_vpu_user.transY, "m"),
                                ("transZ", self.extrinsic_vpu_user.transZ, "m")
                            ],
                            ""
                        ),
                        horizontalalignment="left", verticalalignment="top")
        self.axtb3 = plt.axes([0.825, 0.175, 0.15, 0.1])
        self.axtb3.xaxis.set_visible(False)
        self.axtb3.yaxis.set_visible(False)
        self.axtb3_invisible = plt.axes([0.825, 0.075, 0.15, 0.2])
        self.axtb3_invisible.axis("off")
        self.axtb3_invisible.text(0.05, 0.95,
                                  "Press \"Start Recording\" to start\nrecording data",
                                  horizontalalignment="left", verticalalignment="top")
        axbt0 = plt.axes([0.8375, 0.75, 0.125, 0.05])
        self.bt0 = Button(axbt0, "Start\nRecording")
        self.cidbt0 = self.bt0.on_clicked(self.__on_click_bt0)
        axbt1 = plt.axes([0.8375, 0.675, 0.125, 0.05])
        self.bt1 = Button(axbt1, "Stop\nRecording")
        axbt2 = plt.axes([0.8375, 0.6, 0.125, 0.05])
        self.bt2 = Button(axbt2, "Estimate\nMisalignment")
        axbt3 = plt.axes([0.8375, 0.1, 0.125, 0.05])
        self.bt3 = Button(axbt3, "Save to VPU")
        axbt4 = plt.axes([0.8375, 0.025, 0.125, 0.05])
        self.bt4 = Button(axbt4, "Close Window")
        self.cidbt4 = self.bt4.on_clicked(self.__on_click_bt4)

    def __clear_plot_axes(self, ts, gyro, ax0, ax1, ax2, window):
        if ts.shape[0] < window:
            ax0.clear()
            ax0.plot(ts, gyro[:, 0], color="tab:blue", label=r"$\omega_x$")
            ax0.legend(loc="upper right")
            ax1.clear()
            ax1.plot(ts, gyro[:, 1], color="tab:blue", label=r"$\omega_y$")
            ax1.legend(loc="upper right")
            ax2.clear()
            ax2.plot(ts, gyro[:, 2], color="tab:blue", label=r"$\omega_z$")
            ax2.legend(loc="upper right")
        else:
            gyro_mean = bn.move_mean(gyro, axis=0, window=window)
            gyro_mean = np.roll(gyro_mean, -(window // 2), axis=0)
            ax0.clear()
            ax0.plot(ts, gyro[:, 0], color="tab:blue", label=r"$\omega_x$")
            ax0.plot(ts, gyro_mean[:, 0], color="tab:orange", label=r"$\omega_{x, SMA}$")
            ax0.legend(loc="upper right")
            ax1.clear()
            ax1.plot(ts, gyro[:, 1], color="tab:blue", label=r"$\omega_y$")
            ax1.plot(ts, gyro_mean[:, 1], color="tab:orange", label=r"$\omega_{y, SMA}$")
            ax1.legend(loc="upper right")
            ax2.clear()
            ax2.plot(ts, gyro[:, 2], color="tab:blue", label=r"$\omega_z$")
            ax2.plot(ts, gyro_mean[:, 2], color="tab:orange", label=r"$\omega_{z, SMA}$")
            ax2.legend(loc="upper right")
        return ax0, ax1, ax2

    def __plausibility_check_extrinsic_calibration(self, ts, accel, gyro, accel_noise, gyro_noise):
        plausible = True

        # There must be standstill during first second of recording
        standstill_duration = 1
        accel_noise_factor = 12
        gyro_noise_factor = 12
        standstill_mask = np.where(ts < standstill_duration)
        accel_std = accel[standstill_mask].std(axis=0)
        gyro_std = gyro[standstill_mask].std(axis=0)
        logger.debug("accel_std: {:.4f}, {:.4f}, {:.4f}".format(*accel_std.tolist()))
        logger.debug("gyro_std: {:.4f}, {:.4f}, {:.4f}".format(*gyro_std.tolist()))
        plausible = np.logical_and(
            plausible,
            np.logical_and(
                np.all(accel_std < accel_noise_factor * accel_noise),
                np.all(gyro_std < gyro_noise_factor * gyro_noise)
            )
        )
        if not plausible:
            logger.warning("Movement detected: There must be standstill during first second of recording")
            return plausible

        # Gravity is expected to act along z-axis
        accel_gravity_abs_diff = 0.5
        gravity = np.array([0.0, 0.0, STANDARD_GRAVITY])
        accel_mean = accel[standstill_mask].mean(axis=0)
        logger.debug("accel_mean: {:.4f}, {:.4f}, {:.4f}".format(*accel_mean.tolist()))
        plausible = np.logical_and(
            plausible,
            np.logical_and(
                np.all((gravity - accel_gravity_abs_diff * np.ones_like(gravity)) < accel_mean),
                np.all(accel_mean < (gravity + accel_gravity_abs_diff * np.ones_like(gravity)))
            )
        )
        if not plausible:
            logger.info("Extrinsic calibration implausible: Gravity is expected to act along z-axis")
            return plausible

        # First movement should be in positive x-direction
        number_connected_indices = 10  # 10 samples corresponds to 0.1 seconds
        movement_accel_threshold = accel_noise_factor * accel_noise  # 0.2
        logger.debug("movement_accel_threshold: {:.4f}".format(movement_accel_threshold))
        movement_indices = np.where(np.abs(accel - accel_mean) > movement_accel_threshold)
        movement_indices_unique = np.unique(movement_indices[0]) if len(movement_indices) > 0 else []
        logger.debug(" ".join(["movement_indices_unique:", ", ".join(["{:d}".format(i) for i in movement_indices_unique])]))
        index_first_movement = -1
        for i in range(len(movement_indices_unique)):
            if i + number_connected_indices < len(movement_indices_unique):
                if movement_indices_unique[i + number_connected_indices] == movement_indices_unique[i] + number_connected_indices:
                    index_first_movement = movement_indices_unique[i]
                    break
        logger.debug("index_first_movement: {:d}".format(index_first_movement))
        if index_first_movement > -1:
            for i in range(number_connected_indices):
                logger.debug("accel[{:d}]: {:.4f}, {:.4f}, {:.4f}".format(
                    index_first_movement + i,
                    *(accel[index_first_movement + i] - accel_mean).tolist()
                ))
            movement_accel_mean = np.mean(accel[index_first_movement:index_first_movement + number_connected_indices] - accel_mean, axis=0)
            movement_accel_median = np.median(accel[index_first_movement:index_first_movement + number_connected_indices] - accel_mean, axis=0)
            logger.debug("movement_accel_mean: {:.4f}, {:.4f}, {:.4f}".format(*(movement_accel_mean.tolist())))
            logger.debug("movement_accel_median: {:.4f}, {:.4f}, {:.4f}".format(*(movement_accel_median.tolist())))
            plausible = np.logical_and(
                plausible,
                np.logical_and(
                    movement_accel_median[0] > 0,
                    np.abs(movement_accel_median[0]) > np.abs(movement_accel_median[1])
                )
            )
        else:
            logger.warning("No movement detected: Unable to perform plausibility check")
            plausible = False
        if not plausible:
            logger.info("Extrinsic calibration implausible: First movement should be in positive x-direction")
            return plausible

        return plausible

    def __plausibility_check_misalignment(self, gyro, alpha, beta):
        plausible = True

        # Misalignment is expected to be small (alpha and beta should be smaller than five degrees)
        misalignment_threshold = 5
        plausible = np.logical_and(
            plausible,
            np.logical_and(
                np.abs(alpha) / np.pi * 180 < misalignment_threshold,
                np.abs(beta) / np.pi * 180 < misalignment_threshold
            )
        )
        if not plausible:
            logger.info("Misalignment implausible: Misalignment is expected to be small")
            return plausible

        # There should be significant rotation (in both directions) around z-axis,
        # while rotation around x- and y-axis should be small
        threshold_rotation = 0.25
        threshold_no_rotation = 0.05
        logger.debug("gyro_min: {:.4f}, {:.4f}, {:.4f}".format(*np.min(gyro, axis=0).tolist()))
        logger.debug("gyro_max: {:.4f}, {:.4f}, {:.4f}".format(*np.max(gyro, axis=0).tolist()))
        plausible = np.logical_and(
            plausible,
            np.logical_and(
                np.logical_and(
                    np.any(gyro[:, 2] > threshold_rotation),
                    np.any(gyro[:, 2] < -threshold_rotation)
                ),
                np.logical_and(
                    np.all(np.abs(gyro[:, 0]) < threshold_no_rotation),
                    np.all(np.abs(gyro[:, 1]) < threshold_no_rotation)
                )
            )
        )
        if not plausible:
            logger.info("Misalignment implausible: There should be significant rotation (in both directions) around z-axis, while rotation around x- and y-axis should be small")
            return plausible

        return plausible

    def __estimate_misalignment(self, gyro):
        def fun(args, gyro):
            alpha, beta = args
            rot_align = CamToWorld.rotMat(alpha, beta, 0)  # tr.euler_matrix(alpha, beta, 0)[:3, :3]
            gyro_aligned = (rot_align @ gyro.transpose()).transpose()
            err = np.linalg.norm(gyro_aligned[:, :2], axis=1)  # only x and y
            logger.debug("RMSE={:.4f}, alpha={:.4f}, beta={:.4f}".format(np.sqrt((err ** 2).mean()), alpha, beta))
            return err

        res = least_squares(fun, x0=[np.pi / 4, np.pi / 4], args=[gyro])
        alpha = res.x[0]
        beta = res.x[1]
        logger.info(" ".join(["Estimated misalignment:", ", ".join(["{:.4f} deg".format(i / np.pi * 180) for i in res.x])]))

        # x = leastsq(fun, x0=[np.pi / 4, np.pi / 4], args=(gyro))
        # res = OptimizeResult()
        # res.x = x[0]
        # alpha = res.x[0]
        # beta = res.x[1]
        # logger.info(" ".join(["Estimated misalignment:", ", ".join(["{:.4f} deg".format(i / np.pi * 180) for i in res.x])]))

        return alpha, beta

    def __on_click_bt0(self, event):
        logger.info("Start recording")
        self.bt0.disconnect(self.cidbt0)  # Disable "Start Recording"
        try:
            self.rcv.connect()
            self.rcv_thread.start()
        except Exception as e:
            logger.error("Unable to connect to VPU (ip: {}, source: {})".format(self.ip, self.source))
        self.anim = FuncAnimation(self.fig, self.__update, interval=20)
        # Redraw immediately (instead of redrawing after moving mouse cursor off button)
        if event.inaxes is not None:
            event.inaxes.figure.canvas.draw_idle()
        self.cidbt1 = self.bt1.on_clicked(self.__on_click_bt1)  # Enable "Stop Recording"
        self.axtb3_invisible.clear()
        self.axtb3_invisible.axis("off")
        self.axtb3_invisible.text(0.05, 0.95,
                                  "Press \"Stop Recording\" to stop\nrecording data",
                                  horizontalalignment="left", verticalalignment="top")

    def __on_click_bt1(self, event):
        logger.info("Stop recording")
        self.bt1.disconnect(self.cidbt1)  # Disable "Start Recording"
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None
        try:
            self.stop_event.set()
            self.rcv_thread.join()
            self.rcv.disconnect()
        except Exception as e:
            self.rcv.rcv = None
        self.axtb3_invisible.clear()
        self.axtb3_invisible.axis("off")
        if self.ts:  # Is ts not empty?
            gyro = np.array([[x, y, z] for x, y, z in zip(self.gyro_x, self.gyro_y, self.gyro_z)])
            accel = np.array([[x, y, z] for x, y, z in zip(self.accel_x, self.accel_y, self.accel_z)])
            self.ax3, self.ax4, self.ax5 = self.__clear_plot_axes(np.array(self.ts), gyro,
                                                                  self.ax3, self.ax4, self.ax5, self.window_mean)
            self.ax3.set_ylabel(r"$\omega$ [rad/s] (original)")
            self.ax3.set_xlabel("$t$ [s]")
            self.ax4.set_xlabel("$t$ [s]")
            self.ax5.set_xlabel("$t$ [s]")
            plausible = self.__plausibility_check_extrinsic_calibration(np.array(self.ts), accel, gyro, self.accel_noise, self.gyro_noise)
            if plausible:
                logger.info("Extrinsic calibration plausible")
                text = "Extrinsic calibration plausible\n\nPress \"Estimate Misalignment\"\nto estimate VPU misalignment"
            else:
                logger.warning("Extrinsic calibration implausible")
                text = "Extrinsic calibration implausible\n\nPress \"Close Window\", see log\nand repeat procedure"
            self.axtb2.clear()
            self.axtb2.xaxis.set_visible(False)
            self.axtb2.yaxis.set_visible(False)
            self.axtb2.text(0.05, 0.95,
                            generate_text_string(
                                "extrinsicVPUToUser (currently\n" +
                                "stored on VPU):",
                                [
                                    ("rotX", self.extrinsic_vpu_user.rotX, "rad"),
                                    ("rotY", self.extrinsic_vpu_user.rotY, "rad"),
                                    ("rotZ", self.extrinsic_vpu_user.rotZ, "rad"),
                                    ("transX", self.extrinsic_vpu_user.transX, "m"),
                                    ("transY", self.extrinsic_vpu_user.transY, "m"),
                                    ("transZ", self.extrinsic_vpu_user.transZ, "m")
                                ],
                                ""
                            ),
                            horizontalalignment="left", verticalalignment="top")
            if plausible:
                self.cidbt2 = self.bt2.on_clicked(self.__on_click_bt2)  # Enable "Estimate Misalignment"
            self.axtb3_invisible.text(0.05, 0.95,
                                      text,
                                      horizontalalignment="left", verticalalignment="top")

    def __on_click_bt2(self, event):
        logger.info("Estimate misalignment")
        self.bt2.disconnect(self.cidbt2)  # Disable "Estimate Misalignment"
        gyro = np.array([[x, y, z] for x, y, z in zip(self.gyro_x, self.gyro_y, self.gyro_z)])
        alpha, beta = self.__estimate_misalignment(gyro)
        rot_align = CamToWorld.rotMat(alpha, beta, 0)  # tr.euler_matrix(alpha, beta, 0)[:3, :3]
        gyro_aligned = (rot_align @ gyro.transpose()).transpose()
        rmse = np.sqrt((np.linalg.norm(gyro_aligned[:, :2], axis=1) ** 2).mean())
        rotX, rotY, rotZ = CamToWorld.rotMatReverse(rot_align @ self.rot_vpu_user)
        ct.memmove(ct.addressof(self.extrinsic_vpu_user_updated),
                   ct.addressof(self.extrinsic_vpu_user),
                   ct.sizeof(AlgoExtrinsicCalibration))
        self.extrinsic_vpu_user_updated.rotX = rotX
        self.extrinsic_vpu_user_updated.rotY = rotY
        self.extrinsic_vpu_user_updated.rotZ = rotZ
        self.ax3, self.ax4, self.ax5 = self.__clear_plot_axes(np.array(self.ts), gyro,
                                                              self.ax3, self.ax4, self.ax5, self.window_mean)
        self.ax3.set_ylabel(r"$\omega$ [rad/s] (original)")
        self.ax3.set_xlabel("$t$ [s]")
        self.ax4.set_xlabel("$t$ [s]")
        self.ax5.set_xlabel("$t$ [s]")
        self.ax0, self.ax1, self.ax2 = self.__clear_plot_axes(np.array(self.ts), gyro_aligned,
                                                              self.ax0, self.ax1, self.ax2, self.window_mean)
        self.ax0.set_ylabel(r"$\omega$ [rad/s] (aligned)")
        plt.setp(self.ax0.get_xticklabels(), visible=False)
        plt.setp(self.ax1.get_xticklabels(), visible=False)
        plt.setp(self.ax2.get_xticklabels(), visible=False)
        plausible = self.__plausibility_check_misalignment(gyro, alpha, beta)
        if plausible:
            logger.info("Estimated misalignment plausible")
            text = "Misalignment plausible\n\nPress \"Save to VPU\" to update\nextrinsic calibration on VPU"
        else:
            logger.warning("Estimated misalignment implausible")
            text = "Misalignment implausible\n\nPress \"Close Window\", see log\nand repeat procedure"
        self.axtb1_invisible.text(0.05, 0.95,
                                  generate_text_string(
                                      "Estimated VPU misalignment:",
                                      [
                                          ("alpha", alpha / np.pi * 180, "deg"),
                                          ("beta", beta / np.pi * 180, "deg"),
                                          ("RMSE", rmse, "rad/s")
                                      ],
                                      ""
                                  ),
                                  horizontalalignment="left", verticalalignment="top")
        self.axtb2.clear()
        self.axtb2.xaxis.set_visible(False)
        self.axtb2.yaxis.set_visible(False)
        self.axtb2.text(0.05, 0.95,
                        generate_text_string(
                            "extrinsicVPUToUser (updated\n" +
                            "based on VPU misalignment):",
                            [
                                ("rotX", self.extrinsic_vpu_user_updated.rotX, "rad"),
                                ("rotY", self.extrinsic_vpu_user_updated.rotY, "rad"),
                                ("rotZ", self.extrinsic_vpu_user_updated.rotZ, "rad"),
                                ("transX", self.extrinsic_vpu_user_updated.transX, "m"),
                                ("transY", self.extrinsic_vpu_user_updated.transY, "m"),
                                ("transZ", self.extrinsic_vpu_user_updated.transZ, "m")
                            ],
                            ""
                        ),
                        horizontalalignment="left", verticalalignment="top")
        if plausible:
            self.cidbt3 = self.bt3.on_clicked(self.__on_click_bt3)  # Enable "Save to VPU"
        self.axtb3_invisible.clear()
        self.axtb3_invisible.axis("off")
        self.axtb3_invisible.text(0.05, 0.95,
                                  text,
                                  horizontalalignment="left", verticalalignment="top")

    def __on_click_bt3(self, event):
        logger.info("Save to VPU")
        self.bt2.disconnect(self.cidbt2)  # Disable "Save to VPU"
        try:
            success = self.xml_rpc.set(self.extrinsic_vpu_user_updated)
            self.axtb2.clear()
            self.axtb2.xaxis.set_visible(False)
            self.axtb2.yaxis.set_visible(False)
            self.axtb2.text(0.05, 0.95,
                            generate_text_string(
                                "extrinsicVPUToUser (currently\n" +
                                "stored on VPU):",
                                [
                                    ("rotX", self.extrinsic_vpu_user_updated.rotX, "rad"),
                                    ("rotY", self.extrinsic_vpu_user_updated.rotY, "rad"),
                                    ("rotZ", self.extrinsic_vpu_user_updated.rotZ, "rad"),
                                    ("transX", self.extrinsic_vpu_user_updated.transX, "m"),
                                    ("transY", self.extrinsic_vpu_user_updated.transY, "m"),
                                    ("transZ", self.extrinsic_vpu_user_updated.transZ, "m")
                                ],
                                ""
                            ),
                            horizontalalignment="left", verticalalignment="top")
        except Exception as e:
            logger.error("Unable to connect to VPU (ip: {}, source: {})".format(self.ip, self.source))
            success = False

        if success:
            text = "Successfully updated extrinsic\ncalibration on VPU\n\nPress \"Close Window\""
        else:
            text = "Unable to update extrinsic\ncalibration on VPU\n\nPress \"Store on VPU\" to retry"

        self.axtb3_invisible.clear()
        self.axtb3_invisible.axis("off")
        self.axtb3_invisible.text(0.05, 0.95,
                                  text,
                                  horizontalalignment="left", verticalalignment="top")

    def __on_click_bt4(self, event):
        logger.info("Close window")
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None
        if self.rcv.rcv is not None:
            try:
                self.stop_event.set()
                self.rcv_thread.join()
                self.rcv.disconnect()
            except Exception as e:
                self.rcv.rcv = None
        self.close()

    def __get_data(self):
        while True:
            try:
                self.rcv.get(self.__callback_rcv)
                if self.stop_event.is_set():
                    break
            except Exception as e:
                break

    def __callback_rcv(self, ifout):
        if not self.ts and ifout.numSamples > 0:  # Is ts still empty?
            self.ts_init = ifout.imuSamples[0].timestamp
            self.gyro_noise = ifout.gyroNoise
            self.accel_noise = ifout.accelNoise
            self.rot_imu_user = CamToWorld.rotMat(ifout.extrinsicIMUToUser.rotX,
                                                  ifout.extrinsicIMUToUser.rotY,
                                                  ifout.extrinsicIMUToUser.rotZ)
        self.ts.extend([float((ifout.imuSamples[i].timestamp - self.ts_init) * 1e-9) for i in range(ifout.numSamples)])
        gyro_imu = np.array([[ifout.imuSamples[i].gyro_x, ifout.imuSamples[i].gyro_y, ifout.imuSamples[i].gyro_z] for i in range(ifout.numSamples)])
        gyro_user = (self.rot_imu_user @ gyro_imu.transpose()).transpose()
        self.gyro_x.extend(gyro_user[:, 0].tolist())
        self.gyro_y.extend(gyro_user[:, 1].tolist())
        self.gyro_z.extend(gyro_user[:, 2].tolist())
        accel_imu = np.array([[ifout.imuSamples[i].accel_x, ifout.imuSamples[i].accel_y, ifout.imuSamples[i].accel_z] for i in range(ifout.numSamples)])
        accel_user = (self.rot_imu_user @ accel_imu.transpose()).transpose()
        self.accel_x.extend(accel_user[:, 0].tolist())
        self.accel_y.extend(accel_user[:, 1].tolist())
        self.accel_z.extend(accel_user[:, 2].tolist())

    def __update(self, frame):
        if len(self.ts) < self.samples_to_display:
            ts = self.ts
            gyro_x = self.gyro_x
            gyro_y = self.gyro_y
            gyro_z = self.gyro_z
        else:
            ts = self.ts[-self.samples_to_display:]
            gyro_x = self.gyro_x[-self.samples_to_display:]
            gyro_y = self.gyro_y[-self.samples_to_display:]
            gyro_z = self.gyro_z[-self.samples_to_display:]

        if len(ts) > 0:
            self.ln0.set_data(ts, gyro_x)
            self.ln1.set_data(ts, gyro_y)
            self.ln2.set_data(ts, gyro_z)

            min_xlim = min(ts)
            max_xlim = max(ts)
            xlim = (min_xlim - 0.1 * (max_xlim - min_xlim), max_xlim + 0.1 * (max_xlim - min_xlim))
            self.ax3.set_xlim(xlim)
            self.ax4.set_xlim(xlim)
            self.ax5.set_xlim(xlim)

            min_ylim = min(gyro_x + gyro_y)
            max_ylim = max(gyro_x + gyro_y)
            ylim = (min_ylim - 0.1 * (max_ylim - min_ylim), max_ylim + 0.1 * (max_ylim - min_ylim))
            self.ax3.set_ylim(ylim)
            self.ax4.set_ylim(ylim)

            min_ylim = min(gyro_z)
            max_ylim = max(gyro_z)
            ylim = (min_ylim - 0.1 * (max_ylim - min_ylim), max_ylim + 0.1 * (max_ylim - min_ylim))
            self.ax5.set_ylim(ylim)

    def show(self):
        plt.show()

    def close(self):
        plt.close()


def get_args():
    parser = argparse.ArgumentParser(description="VPU Misalignment Estimation")

    parser.add_argument("--ip", help="IP address of VPU", default="192.168.0.69")
    parser.add_argument("--source", help="Algo debug source", default="port6", choices=[("port%d" % v) for v in range(7)])

    args = parser.parse_args(sys.argv[1:])
    return args


def main():
    args = get_args()
    ip = args.ip
    source = args.source

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(console)
    logger.setLevel(logging.INFO)

    gui = VPUMisalignmentEstimationGUI(ip, source)
    try:
        gui.show()
    except Exception as e:
        raise e
    finally:
        gui.close()


if __name__ == "__main__":
    main()
