#############################################
# Copyright 2023-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################

# This file can be run interactively, section by section
# Sections are delimited by '#%%'
# Several editors including Spyder and vscode+python are equiped to run these cells
# by simply pressing shift-enter

# %%
import ifm3dpy
from ifm3dpy import buffer_id, FrameGrabber, O3R
import numpy as np
import cv2

import time

DEFAULT_BUFFERS_OF_INTEREST = {
    "3D": {
        "dist": buffer_id.RADIAL_DISTANCE_IMAGE,
        "NAI": buffer_id.NORM_AMPLITUDE_IMAGE,
    },
    "2D": {
        "rgb": buffer_id.JPEG_IMAGE,
    },
}


class FrameCollector:
    def __init__(
        self,
        o3r,
        ports: list = [],
        timeout=0.25,
        buffers_of_interest=DEFAULT_BUFFERS_OF_INTEREST,
    ):
        self.ifm3dpy_v = [int(v) for v in ifm3dpy.__version__.split(".")]

        self.o3r = o3r

        self.port_config = o3r.get()

        if len(ports) != 0:
            port_ns = ports
        else:
            available_ports = list(self.port_config["ports"].keys())
            available_ports_sans_imu = []
            for port in available_ports:
                if int(port[-1]) < 6:
                    available_ports_sans_imu.append(port)
            port_ns = [int(port_name[-1]) for port_name in available_ports_sans_imu]
        self.port_ns = port_ns

        self.sensor_types = {}
        for port_n in port_ns:
            self.sensor_types[port_n] = self.port_config["ports"][f"port{port_n}"][
                "info"
            ]["features"]["type"]

        self.buffer_ids_of_interest = {}
        for port_n in port_ns:
            self.buffer_ids_of_interest[port_n] = buffers_of_interest[
                self.sensor_types[port_n]
            ]

        self.frame_grabbers = {}
        for port_n in port_ns:
            self.frame_grabbers[port_n] = FrameGrabber(o3r, 50010 + port_n)
            self.frame_grabbers[port_n].start(
                list(self.buffer_ids_of_interest[port_n].values())
            )

        self.saved_buffer_sets = []
        self.buffer_data_set = {port_n: {} for port_n in self.port_ns}

    def loop(self, timeout=2000):
        # set cameras to run
        o3r_port_json = {}
        for port_n in self.port_ns:
            o3r_port_json.update({f"port{port_n}": {"state": "RUN"}})
        self.o3r.set({"ports": o3r_port_json})
        time.sleep(0.1)

        # start opencv windows
        for port_n in self.port_ns:
            for buffer_name in self.buffer_ids_of_interest[port_n].keys():
                cv2.namedWindow(f"{buffer_name} - port {port_n}", cv2.WINDOW_NORMAL)

        # prep for using cv2.putText() method
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (10, 10)
        fontScale = 0.7
        color = (255, 255, 0)
        thickness = 2

        # collect buffers
        while True:
            frames = {}
            key_presses = []
            for port_n in self.port_ns:
                ret, frame = (
                    self.frame_grabbers[port_n].wait_for_frame().wait_for(timeout)
                )
                frames[port_n] = frame
                for buffer_name, buffer_id in self.buffer_ids_of_interest[
                    port_n
                ].items():
                    buffer_data = frame.get_buffer(buffer_id)

                    # some additional boilerplate for unpacking 2D data
                    if self.sensor_types[port_n] == "2D" and buffer_name == "rgb":
                        buffer_data = cv2.imdecode(buffer_data, cv2.IMREAD_UNCHANGED)

                    self.buffer_data_set[port_n][buffer_name] = buffer_data
                    winname = f"{buffer_name} - port {port_n}"

                    text_overlay = "Press 's' to record for analysis"
                    if len(buffer_data.shape) < 3:
                        buffer_data_color = cv2.cvtColor(
                            buffer_data.copy(), cv2.COLOR_GRAY2BGR
                        )
                    else:
                        buffer_data_color = buffer_data.copy()
                    buffer_data_with_text = cv2.putText(
                        buffer_data_color,
                        text_overlay,
                        np.array(
                            (np.array((0, 0.1)) * buffer_data.shape[0]), np.uint16
                        ).tolist(),
                        fontFace=font,
                        fontScale=fontScale * buffer_data.shape[0] / 300,
                        color=color,
                        thickness=int(thickness * buffer_data.shape[0] / 300),
                    )
                    cv2.imshow(winname, buffer_data_with_text)
                    key_presses.append(cv2.waitKey(1))

            # check for save
            if ord("s") in key_presses:
                self.saved_buffer_sets.append(self.buffer_data_set.copy())

                for port_n, saved_buffers in self.buffer_data_set.items():
                    for buffer_name, buffer_data in saved_buffers.items():
                        winname = f"{buffer_name} - port {port_n} - Saved"
                        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)

                        text_overlay = "Press 'Esc' to use this frame."
                        if len(buffer_data.shape) < 3:
                            buffer_data_color = cv2.cvtColor(
                                buffer_data.copy(), cv2.COLOR_GRAY2BGR
                            )
                        else:
                            buffer_data_color = buffer_data.copy()
                        buffer_data_with_text = cv2.putText(
                            buffer_data_color,
                            text_overlay,
                            org,
                            fontFace=font,
                            fontScale=fontScale * buffer_data.shape[0] / 300,
                            color=color,
                            thickness=int(thickness * buffer_data.shape[0] / 300),
                        )
                        cv2.imshow(winname, buffer_data_with_text)

            # check for exit
            if 27 in key_presses:
                # reset the port_config and cleanup
                self.o3r.set(self.port_config)
                cv2.destroyAllWindows()
                break


# %%
if __name__ == "__main__":
    IP_ADDR = "192.168.0.69"

    o3r = O3R(IP_ADDR)

    frame_collector = FrameCollector(o3r)
    frame_collector.loop()
