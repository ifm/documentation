#############################################
# Copyright 2021-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################

import json
import logging
import pathlib
from jsonschema import exceptions as json_exceptions
from jsonschema import validate
from ifm3dpy.device import Error as ifm3dpy_error
from ifm3dpy.device import O3R


class ODSConfig:
    """Provides functions showcasing how to handle json configuration
    of an O3R device, using the ifm3dpy library.
    """

    def __init__(self, o3r: O3R) -> None:
        self.o3r = o3r
        self.schema = o3r.get_schema()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            format="%(asctime)s:%(filename)-10s:%(levelname)-8s:%(message)s",
            datefmt="%y-%m-%d %H:%M:%S",
        )
        self.logger.setLevel(logging.DEBUG)

    def validate_json(self, config: json) -> bool:
        """This function can be used to validate
        a configuration before setting it.
        Note that ifm3dpy.device.O3R.set() will validate the
        requested configuration, but using the jsonschema.validate
        function will provide a more verbose validation.

        :param config: the configuration to validate
        :raises ValidationError: if the validation fails
        """
        try:
            self.logger.info(f"Validating configuration")
            validate(config, self.schema)
        except json_exceptions.ValidationError as err:
            self.logger.exception("Error while validating the json schema")
            raise err
        except json_exceptions.SchemaError as err:
            self.logger.exception("Incorrect json schema")
            raise err

    def set_config_from_file(self, config_file: pathlib.Path):
        """Configure the device from a configuration file.
        The provided configuration is validated using the schema validator.

        :param config_file: path to the configuration file
        """
        try:
            self.logger.info(f"Loading configuration from file {config_file}")
            with open(config_file, "r") as f:
                config = json.load(f)
            # This function will validate the configuration against the schema
            # and apply it to the O3R.
            self.set_config_from_dict(config)
        except OSError as err:
            self.logger.exception("Error while reading configuration file")
            raise err

    def set_config_from_dict(self, config: json):
        """Configure the device provided a configuration dictionary.
        The provided configuration is validated using the schema validator.

        :param config: dictionary of the desired configuration
        :raises ifm3dpy.device.Error: if the configuration fails
        """
        try:
            self.validate_json(config)
            self.logger.info(f"Setting configuration {config}")
            self.o3r.set(config)
        except ifm3dpy_error as err:
            self.logger.exception("Error while configurating device")
            raise err

    def get(self, config_path=[""]):
        """Get current configuration fragment, provided the expected dictionary.
        If nothing is provided, the full configuration will be returned.
        Note that this function can be used exactly as the ifm3dpy.device.O3R.get() function
        :param config_path: fragment of configuration to retrieve
        :return: the configuration
        :raises ifm3dpy.device.Error: if the configuration cannot be retrieved
        """
        try:
            self.logger.info(f"Getting configuration at {config_path}")
            return self.o3r.get(config_path)
        except ifm3dpy_error as err:
            self.logger.exception("Error while getting configuration")
            raise err


def main():
    """
    Example on how to use the ODSConfig class.
    Make sure you configure the IP address for your specific setup.
    """
    IP = "192.168.0.69"
    o3r = O3R(IP)
    ods_config = ODSConfig(o3r=o3r)
    #############################################
    # Examples on getting configurations snippets
    #############################################
    ods_config.logger.info(ods_config.get())  # Get the full configuration
    ods_config.logger.info(
        ods_config.get(
            ["/device/swVersion/firmware"]
        )  # Get a subset of the configuration
    )
    ods_config.logger.info(
        ods_config.get(
            ["/device/swVersion/firmware", "/device/status", "/ports/port0/info"]
        )  # Get multiple fragments of the configuration
    )
    try:  # This will throw an exception
        ods_config.logger.info(ods_config.get(["/device/wrongkey"]))
    # Failing silently to continue through the examples
    except ifm3dpy_error:
        pass
    #####################################
    # Examples on setting configurations
    #####################################
    ods_config.set_config_from_dict(
        {"device": {"info": {"description": "I will use this O3R to change the world"}}}
    )
    ods_config.set_config_from_dict(  # Set two configuration fragments at the same time
        {
            "device": {"info": {"name": "my_favorite_o3r"}},
            "ports": {"port0": {"info": {"name": "my_favorite_port"}}},
        }  # Assume port connected in port0
    )
    try:  # This will throw an exception
        ods_config.set_config_from_dict({"device": {"info": {"description": 0}}})
    # Failing silently to continue through the examples
    except json_exceptions.ValidationError:
        pass

    ods_config.set_config_from_file("configs/ods_one_head_config.json")
    try:  # This will throw an exception
        ods_config.set_config_from_file("non/existent/file.json")
    # Failing silently to continue through the examples
    except OSError:
        pass

    ods_config.logger.info("You reached the end of the ODSConfig tutorial!")


if __name__ == "__main__":
    main()
