import argparse
import logging
import sys

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, TextBox
from o3r_algo_utilities.calib.vpu.vpu_misalignment_estimation import AlgoExtrinsicCalibration, round_floats, generate_text_string, VPUExtrinsicCalibrationXMLRPC

logger = logging.getLogger(__name__)

plt.rcParams["toolbar"] = "None"  # Disable toolbar


class VPUExtrinsicCalibrationGUI:
    def __init__(self, ip, source):
        self.ip = ip
        self.source = source

        try:
            assert self.source == "port6"
            self.xml_rpc = VPUExtrinsicCalibrationXMLRPC(self.ip, self.source, True, "experimental_ods")
            self.extrinsic_vpu_user = self.xml_rpc.get()
            self.extrinsic_vpu_user_updated = AlgoExtrinsicCalibration()
        except Exception as e:
            logger.error("Unable to connect to VPU (ip: {}, source: {})".format(self.ip, self.source))
            return  # Return immediately

        self.rot_array = np.array([
            [0, 0, 0],  # Added to match ID
            [0, 0, 0],
            [0, 0, np.pi / 2],
            [0, 0, np.pi],
            [0, 0, -np.pi / 2],
            [np.pi / 2, 0, 0],
            [np.pi / 2, np.pi / 2, 0],
            [np.pi / 2, np.pi, 0],
            [np.pi / 2, -np.pi / 2, 0],
            [np.pi, 0, 0],
            [np.pi, 0, np.pi / 2],
            [np.pi, 0, np.pi],
            [np.pi, 0, -np.pi / 2],
            [-np.pi / 2, 0, 0],
            [-np.pi / 2, np.pi / 2, 0],
            [-np.pi / 2, np.pi, 0],
            [-np.pi / 2, -np.pi / 2, 0],
            [0, np.pi / 2, np.pi],
            [0, -np.pi / 2, np.pi],
            [0, np.pi / 2, 0],
            [0, -np.pi / 2, 0],
            [-np.pi / 2, 0, np.pi / 2],
            [np.pi / 2, 0, np.pi / 2],
            [-np.pi / 2, 0, -np.pi / 2],
            [np.pi / 2, 0, -np.pi / 2]
        ])

        self.id = 0
        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 0
        self.trans_x = 0
        self.trans_y = 0
        self.trans_z = 0

        self.fig = None
        self.axtb_id = None
        self.tb_id = None
        self.axtb_rot_x = None
        self.tb_rot_x = None
        self.axtb_rot_y = None
        self.tb_rot_y = None
        self.axtb_rot_z = None
        self.tb_rot_z = None
        self.axtb_trans_x = None
        self.tb_trans_x = None
        self.axtb_trans_y = None
        self.tb_trans_y = None
        self.axtb_trans_z = None
        self.tb_trans_z = None
        self.bt_update = None  # "Update"
        self.bt_save = None  # "Save to VPU"
        self.bt_close = None  # "Close Window"
        self.cid_bt_update = 0
        self.cid_bt_save = 0
        self.cid_bt_close = 0
        self.axtb_extrinsic_left = None
        self.axtb_extrinsic_right = None

        self.__setup_fig()

    def __setup_fig(self):
        self.fig = plt.figure("VPU Extrinsic Calibration", figsize=(12.0, 7.2), dpi=72)
        self.fig.tight_layout()

        cell_text = [
            [1, "0", "0", "0", "to the right", "$-Y_{U}$", "upwards", "$+Z_{U}$"],
            [2, "0", "0", "$\pi/2$", "to the front", "$+X_{U}$", "upwards", "$+Z_{U}$"],
            [3, "0", "0", "$\pi$", "to the left", "$+Y_{U}$", "upwards", "$+Z_{U}$"],
            [4, "0", "0", "$-\pi/2$", "to the back", "$-X_{U}$", "upwards", "$+Z_{U}$"],
            [5, "$\pi/2$", "0", "0", "downwards", "$-Z_{U}$", "to the right", "$-Y_{U}$"],
            [6, "$\pi/2$", "$\pi/2$", "0", "downwards", "$-Z_{U}$", "to the front", "$+X_{U}$"],
            [7, "$\pi/2$", "$\pi$", "0", "downwards", "$-Z_{U}$", "to the left", "$+Y_{U}$"],
            [8, "$\pi/2$", "$-\pi/2$", "0", "downwards", "$-Z_{U}$", "to the back", "$-X_{U}$"],
            [9, "$\pi$", "0", "0", "to the left", "$+Y_{U}$", "downwards", "$-Z_{U}$"],
            [10, "$\pi$", "0", "$\pi/2$", "to the front", "$+X_{U}$", "downwards", "$-Z_{U}$"],
            [11, "$\pi$", "0", "$\pi$", "to the right", "$-Y_{U}$", "downwards", "$-Z_{U}$"],
            [12, "$\pi$", "0", "$-\pi/2$", "to the back", "$-X_{U}$", "downwards", "$-Z_{U}$"],
            [13, "$-\pi/2$", "0", "0", "upwards", "$+Z_{U}$", "to the left", "$+Y_{U}$"],
            [14, "$-\pi/2$", "$\pi/2$", "0", "upwards", "$+Z_{U}$", "to the front", "$+X_{U}$"],
            [15, "$-\pi/2$", "$\pi$", "0", "upwards", "$+Z_{U}$", "to the right", "$-Y_{U}$"],
            [16, "$-\pi/2$", "$-\pi/2$", "0", "upwards", "$+Z_{U}$", "to the back", "$-X_{U}$"],
            [17, "0", "$\pi/2$", "$\pi$", "to the left", "$+Y_{U}$", "to the front", "$+X_{U}$"],
            [18, "0", "$-\pi/2$", "$\pi$", "to the left", "$+Y_{U}$", "to the back", "$-X_{U}$"],
            [19, "0", "$\pi/2$", "0", "to the right", "$-Y_{U}$", "to the front", "$+X_{U}$"],
            [20, "0", "$-\pi/2$", "0", "to the right", "$-Y_{U}$", "to the back", "$-X_{U}$"],
            [21, "$-\pi/2$", "0", "$\pi/2$", "to the front", "$+X_{U}$", "to the left", "$+Y_{U}$"],
            [22, "$\pi/2$", "0", "$\pi/2$", "to the front", "$+X_{U}$", "to the right", "$-Y_{U}$"],
            [23, "$-\pi/2$", "0", "$-\pi/2$", "to the back", "$-X_{U}$", "to the left", "$+Y_{U}$"],
            [24, "$\pi/2$", "0", "$-\pi/2$", "to the back", "$-X_{U}$", "to the right", "$-Y_{U}$"]
        ]
        col_labels = [
            "ID",
            "rotX\n[rad]",
            "rotY\n[rad]",
            "rotZ\n[rad]",
            "VPU plugs\ndirection\n(desc.)",
            "VPU plugs\ndirection\n(math.)",
            "VPU labels\ndirection\n(desc.)",
            "VPU labels\ndirection\n(math.)"
        ]
        ax_table = self.fig.add_axes([0, 0, 1, 1])
        table = ax_table.table(cellText=cell_text, colLabels=col_labels, loc="upper left", edges="horizontal")
        table.auto_set_font_size(False)
        cell_dict = table.get_celld()
        for col in range(0, len(col_labels)):
            cell_dict[(0, col)].set_height(cell_dict[(0, col)].get_height() * 5)
            for row in range(0, len(cell_text)):
                cell_dict[(row + 1, col)].set_height(cell_dict[(row + 1, col)].get_height() * 1.5)
        for row in range(0, len(cell_text) + 1):
            col_width_factors = [0.25, 0.5, 0.5, 0.5, 0.75, 0.5, 0.75, 0.5]
            for col in range(0, len(col_labels)):
                cell_dict[(row, col)].set_width(cell_dict[(row, col)].get_width() * col_width_factors[col])

        ax_description = self.fig.add_axes([0.575, 0.7, 0.2, 0.275])
        ax_description.axis("off")
        ax_description.text(0.5, 0.5,
                            "Provide measurements for extrinsic\n" +
                            "VPU calibration (rotX, rotY, rotZ,\n" +
                            "transX, transY, transZ)\n" +
                            "\n" +
                            "Orientation can be determined based\n"
                            "on table on the left by identifying\n" +
                            "direction of VPU plugs and labels\n" +
                            "(for axis-aligned mounting positions)\n" +
                            "Translation must be measured manually\n"
                            "\n" +
                            "\"Update\" updates the extrinsic VPU\n" +
                            "calibration before it is stored on\n" +
                            "VPU with \"Save to VPU\"",
                            horizontalalignment="center", verticalalignment="center")

        vpu_image = plt.imread("images/ovp800.png")
        ax_vpu_image = self.fig.add_axes([0.8, 0.725, 0.2, 0.2])
        ax_vpu_image.axis("off")
        ax_vpu_image.imshow(vpu_image)

        self.axtb_id = self.fig.add_axes([0.625, 0.625, 0.125, 0.05])
        self.tb_id = TextBox(self.axtb_id, "ID", label_pad=0.1, textalignment="center")
        self.axtb_rot_x = self.fig.add_axes([0.625, 0.55, 0.125, 0.05])
        self.tb_rot_x = TextBox(self.axtb_rot_x, "rotX\n[rad]", label_pad=0.1, textalignment="center")
        self.axtb_rot_y = self.fig.add_axes([0.625, 0.475, 0.125, 0.05])
        self.tb_rot_y = TextBox(self.axtb_rot_y, "rotY\n[rad]", label_pad=0.1, textalignment="center")
        self.axtb_rot_z = self.fig.add_axes([0.625, 0.4, 0.125, 0.05])
        self.tb_rot_z = TextBox(self.axtb_rot_z, "rotZ\n[rad]", label_pad=0.1, textalignment="center")
        self.axtb_trans_x = self.fig.add_axes([0.85, 0.55, 0.125, 0.05])
        self.tb_trans_x = TextBox(self.axtb_trans_x, "transX\n[m]", label_pad=0.1, textalignment="center")
        self.axtb_trans_y = self.fig.add_axes([0.85, 0.475, 0.125, 0.05])
        self.tb_trans_y = TextBox(self.axtb_trans_y, "transY\n[m]", label_pad=0.1, textalignment="center")
        self.axtb_trans_z = self.fig.add_axes([0.85, 0.4, 0.125, 0.05])
        self.tb_trans_z = TextBox(self.axtb_trans_z, "transZ\n[m]", label_pad=0.1, textalignment="center")

        self.tb_id.on_submit(self.__submit_id)
        self.tb_rot_x.on_submit(self.__submit_rot_x)
        self.tb_rot_y.on_submit(self.__submit_rot_y)
        self.tb_rot_z.on_submit(self.__submit_rot_z)
        self.tb_trans_x.on_submit(self.__submit_trans_x)
        self.tb_trans_y.on_submit(self.__submit_trans_y)
        self.tb_trans_z.on_submit(self.__submit_trans_z)

        self.tb_id.set_val(0)
        self.tb_trans_x.set_val(0.0)
        self.tb_trans_y.set_val(0.0)
        self.tb_trans_z.set_val(0.0)

        axbt_update = plt.axes([0.825, 0.625, 0.125, 0.05])
        self.bt_update = Button(axbt_update, "Update")
        self.cid_bt_update = self.bt_update.on_clicked(self.__on_click_bt_update)
        axbt_save = plt.axes([0.7125, 0.1, 0.125, 0.05])
        self.bt_save = Button(axbt_save, "Save to VPU")
        self.cid_bt_save = self.bt_save.on_clicked(self.__on_click_bt_save)
        axbt_close = plt.axes([0.7125, 0.025, 0.125, 0.05])
        self.bt_close = Button(axbt_close, "Close Window")
        self.cid_bt_close = self.bt_close.on_clicked(self.__on_click_bt_close)

        self.axtb_extrinsic_left = plt.axes([0.575, 0.175, 0.175, 0.2])
        self.axtb_extrinsic_right = plt.axes([0.8, 0.175, 0.175, 0.2])
        self.__update()

    def __update(self):
        try:
            self.extrinsic_vpu_user = self.xml_rpc.get()
        except Exception as e:
            logger.error("Unable to connect to VPU (ip: {}, source: {})".format(self.ip, self.source))
        self.extrinsic_vpu_user_updated.rotX = self.rot_x
        self.extrinsic_vpu_user_updated.rotY = self.rot_y
        self.extrinsic_vpu_user_updated.rotZ = self.rot_z
        self.extrinsic_vpu_user_updated.transX = self.trans_x
        self.extrinsic_vpu_user_updated.transY = self.trans_y
        self.extrinsic_vpu_user_updated.transZ = self.trans_z
        self.axtb_extrinsic_left.clear()
        self.axtb_extrinsic_left.xaxis.set_visible(False)
        self.axtb_extrinsic_left.yaxis.set_visible(False)
        self.axtb_extrinsic_left.text(0.05, 0.95,
                                      generate_text_string(
                                          "extrinsicVPUToUser\n" +
                                          "(currently stored on VPU):",
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
        self.axtb_extrinsic_right.clear()
        self.axtb_extrinsic_right.xaxis.set_visible(False)
        self.axtb_extrinsic_right.yaxis.set_visible(False)
        self.axtb_extrinsic_right.text(0.05, 0.95,
                                       generate_text_string(
                                           "extrinsicVPUToUser\n" +
                                           "(will be stored on VPU):",
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

    def __submit_id(self, expression):
        self.id = int(eval(expression))
        logger.debug("Submit id (id={:d})".format(self.id))
        self.rot_x = self.rot_array[self.id, 0]
        self.tb_rot_x.set_val(round_floats(self.rot_x, 4))
        self.rot_y = self.rot_array[self.id, 1]
        self.tb_rot_y.set_val(round_floats(self.rot_y, 4))
        self.rot_z = self.rot_array[self.id, 2]
        self.tb_rot_z.set_val(round_floats(self.rot_z, 4))

    def __submit_rot_x(self, expression):
        self.rot_x = float(eval(expression))
        logger.debug("Submit rot_x (rot_x={:.4f})".format(self.rot_x))

    def __submit_rot_y(self, expression):
        self.rot_y = float(eval(expression))
        logger.debug("Submit rot_y (rot_y={:.4f})".format(self.rot_y))

    def __submit_rot_z(self, expression):
        self.rot_z = float(eval(expression))
        logger.debug("Submit rot_z (rot_z={:.4f})".format(self.rot_z))

    def __submit_trans_x(self, expression):
        self.trans_x = float(eval(expression))
        logger.debug("Submit trans_x (trans_x={:.4f})".format(self.trans_x))

    def __submit_trans_y(self, expression):
        self.trans_y = float(eval(expression))
        logger.debug("Submit trans_y (trans_y={:.4f})".format(self.trans_y))

    def __submit_trans_z(self, expression):
        self.trans_z = float(eval(expression))
        logger.debug("Submit trans_z (trans_z={:.4f})".format(self.trans_z))

    def __on_click_bt_update(self, event):
        logger.info("Update")
        self.__update()

    def __on_click_bt_save(self, event):
        logger.info("Save to VPU")
        try:
            success = self.xml_rpc.set(self.extrinsic_vpu_user_updated)
            assert success
        except Exception as e:
            logger.error("Unable to connect to VPU (ip: {}, source: {})".format(self.ip, self.source))
        self.__update()

    def __on_click_bt_close(self, event):
        logger.info("Close window")
        self.close()

    def show(self):
        plt.show()

    def close(self):
        plt.close()


def get_args():
    parser = argparse.ArgumentParser(description="VPU Extrinsic Calibration")

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

    gui = VPUExtrinsicCalibrationGUI(ip, source)
    try:
        gui.show()
    except Exception as e:
        raise e
    finally:
        gui.close()


if __name__ == "__main__":
    main()
