#############################################
# Copyright 2023-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################

import pathlib

# This port mapping below only applies for a fully connected VPU, that is all ports starting from 0 have an imager connected to it
PORT_TEMPERATURE_MAPPING = {  # (1)
    "port0": 8,
    "port1": 9,
    "port2": 10,
    "port3": 11,
    "port4": 12,
    "port5": 13,
}

BUFFER_LENGTH = 50  # (2))

RECORDING_TIME = 10  # (3)

INTERVAL = 200  # (4)

SCHEMA = {  # (5)
    "layouter": "flexible",
    "format": {"dataencoding": "ascii"},
    "elements": [
        {"type": "string", "value": "star", "id": "start_string"},
        {"type": "blob", "id": "O3R_ODS_OCCUPANCY_GRID"},
        {"type": "blob", "id": "O3R_ODS_INFO"},
        {"type": "string", "value": "stop", "id": "end_string"},
    ],
}

CURRENT_DIR = pathlib.Path(__file__).parent.resolve()  # (5)
ODS_CONFIG_JSON_TWO_HEADS = CURRENT_DIR / "configs" / "ods_two_heads_config.json"
ODS_CONFIG_JSON_ONE_HEADS = CURRENT_DIR / "configs" / "ods_one_head_config.json"
ODS_CONFIG_JSON_ONE_HEADS_EXTRINSICS = (
    CURRENT_DIR / "configs" / "ods_one_head_config_extrinsic.json"
)
ODS_WHOLE_CONFIG = CURRENT_DIR / "configs" / "ods_config_complete.json"
ODS_EXTRINSIC_CALIBRATION_TWO_HEADS = (
    CURRENT_DIR / "configs" / "extrinsic_two_heads.json"
)
ODS_ERROR_DICT = CURRENT_DIR / "helper" / "ods_error_list.json"
ODS_WHOLE_CONFIG_OL = CURRENT_DIR / "configs" / "ods_config_complete_ol.json"
# EXTRINSIC 0
extrinsic_calib_0 = {
    "processing": {
        "extrinsicHeadToUser": {
            "rotX": -0.3,
            "rotY": 0.0,
            "rotZ": 1.57,
            "transX": 0.1,
            "transY": 0.1,
            "transZ": 0.1,
        }
    }
}
extrinsic_calib_0_zone = [[[1.0, 1.0], [1.0, 0.0], [-1.0, 0.0], [-1.0, 1.0]]]
extrinsic_calib_0_zone = [
    [[0, 1.0], [1.0, 1], [1, -1], [0, -1]],
    [[1, 1], [2, 1], [2, -1], [1, -1]],
]
# extrinsic_calib_0_zone = [[[0, 1.0], [1.0, 1], [1, -1], [0, -1]], [[1, 1], [2, 1], [2, -1], [1, -1]], [[2, 1], [3, 1], [3, -1], [2, -1]]]

extrinsic_calib_0_zone_out = True
extrinsic_0 = {
    "calib": extrinsic_calib_0,
    "zone": extrinsic_calib_0_zone,
    "out": extrinsic_calib_0_zone_out,
    "desc": "default for ODS test",
}
MIN_PROBABILITY = 0.5  # TODO: get value as configured in ODS application
