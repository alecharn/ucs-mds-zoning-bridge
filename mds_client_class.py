#!/usr/bin/env python3

"""
This module defines the `MdsClient` class to interact with Cisco MDS NX-API.

Author:
    Adrien LECHARNY - April 2025
"""

# Standard library imports
import json
import sys

# Third-party library imports
import requests
import urllib3

# Local application imports
from base_logger import logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##############################################################################
#                              MDSClient class                               #
##############################################################################


class MdsClient:
    """
    Class to interact with MDS NX-API.

    This class provides various methods to interact with the MDS switch using NX-API.

    Attributes:
        mds_ip_address (str): IP address of the MDS switch.
        mds_username (str): Username for authentication.
        mds_password (str): Password for authentication.
        api_headers (dict): Headers for API requests.
        api_payload (dict): Payload for API requests.
        api_timeout (int): Timeout for API requests.
        api_type_config (str): Type of configuration command.
        api_type_show (str): Type of show command.
        api_url (str): URL for API requests.
        api_verify (bool): SSL verification flag.
    """

    # Class variables
    def __init__(self, mds_ip_address: str, mds_username: str, mds_password: str):
        """
        Initialize the MdsClient class.

        Args:
            mds_ip_address (str): IP address of the MDS switch.
            mds_username (str): Username for authentication.
            mds_password (str): Password for authentication.
        """

        logger.info(
            "Initializing `MDSClient` instance with IP address '%s' and username '%s'.\n",
            mds_ip_address,
            mds_username,
        )

        # Validate the MDS IP address
        if not mds_ip_address:
            logger.error("MDS IP address is not provided.\n")
            sys.exit(1)

        # Validate the MDS username
        if not mds_username:
            logger.error("MDS username is not provided.\n")
            sys.exit(1)

        # Validate the MDS password
        if not mds_password:
            logger.error("MDS password is not provided.\n")
            sys.exit(1)

        # Set the MDS switch IP address and credentials
        self.ip_address = mds_ip_address
        self.username = mds_username
        self.password = mds_password

        # Set the API headers and URL
        self.api_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.api_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "",
                "chunk": "0",
                "sid": "1",
                "input": "",
                "output_format": "json",
            }
        }
        self.api_timeout = 10
        self.api_type_config = "cli_conf"
        self.api_type_show = "cli_show"
        self.api_url = f"https://{self.ip_address}:8443/ins"
        self.api_verify = False

    # Method to send POST requests to the MDS switch
    def post_request(self, request_input: str, request_type: str):
        """
        Send a POST request to the MDS switch.

        Args:
            request_input (str): Input command to be sent.
            request_type (str): Type of command.

        Returns:
            response (requests.Response): Response object from the POST request.
        """

        payload = self.api_payload
        payload["ins_api"]["input"] = request_input
        payload["ins_api"]["type"] = request_type

        logger.info(
            "Sending POST request to MDS switch of type '%s' with input '%s'.\n",
            request_type,
            request_input,
        )

        # Debug logging
        logger.debug(
            "POST Request Details:\nPayload: %s\nHeaders: %s\nURL: %s\nTimeout: %s\nVerify SSL: %s\n",
            json.dumps(payload, indent=4),
            self.api_headers,
            self.api_url,
            self.api_timeout,
            self.api_verify,
        )

        # POST Request
        response = requests.post(
            self.api_url,
            data=json.dumps(payload),
            headers=self.api_headers,
            auth=(self.username, self.password),
            timeout=self.api_timeout,
            verify=self.api_verify,
        )

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            logger.info(
                "POST request of type '%s' with input '%s' to MDS `%s`was successful.\n",
                self.ip_address,
                request_type,
                request_input,
            )

            logger.debug(
                "Response Details from MDS `%s`:\nStatus Code: %s\nContent: %s\n",
                self.ip_address,
                response.status_code,
                json.dumps(response.json(), indent=4),
            )

        else:
            logger.error(
                "POST request failed with status code: '%s' and response content: '%s'.\n",
                response.status_code,
                response.json(),
            )
            sys.exit(1)

        # Check CLI error in the content of response the code
        if "code" in response.json()["ins_api"]["outputs"]["output"]:
            if response.json()["ins_api"]["outputs"]["output"]["code"] != "200":

                logger.error(
                    "CLI command pushed to MDS `%s` generated the following error:%s\n",
                    self.ip_address,
                    response.json()["ins_api"]["outputs"]["output"],
                )

        return response

    # Method to activate a zoneset on the MDS switch
    def activate_zoneset(self, zoneset_name: str, vsan_id: str):
        """
        Activate a zoneset on the MDS switch.

        Args:
            zoneset_name (str): Name of the zoneset.
            vsan_id (str): VSAN ID.

        Returns:
            response (json): JSON response from the MDS switch.
        """

        logger.info(
            "Activating zoneset '%s' in VSAN '%s'.\n",
            zoneset_name,
            vsan_id,
        )

        # Construct the command to activate zoneset
        command = f"zoneset activate name {zoneset_name} vsan {vsan_id}"
        logger.info("Constructed command to activate zoneset: '%s'.\n", command)

        # Send the POST request
        response = self.post_request(
            request_input=command, request_type=self.api_type_config
        )

        return response.json()

    # Method to add device alias to the MDS switch
    def add_device_alias(self, device_alias_name: str, wwpn: str):
        """
        Add a device-alias to the MDS switch associated with a WWPN.

        Args:
            device_alias_name (str): Name of the device-alias.
            wwpn (str): WWPN of the device.

        Returns:
            response (json): JSON response from the MDS switch.
        """

        logger.info(
            "Adding device alias '%s' with WWPN '%s'.\n",
            device_alias_name,
            wwpn,
        )

        # Construct the command to add device alias
        command = f"device-alias database ;device-alias name {device_alias_name} pwwn {wwpn} ;device-alias commit"
        logger.info("Constructed command to add device alias: '%s'.\n", command)

        # Send the POST request
        response = self.post_request(
            request_input=command, request_type=self.api_type_config
        )

        return response.json()

    # Method to add zone to zoneset on the MDS switch
    def add_zone_to_zoneset(self, zone_name: str, zoneset_name: str, vsan_id: str):
        """
        Add a zone to a zoneset on the MDS switch in a specific VSAN.
        If zone does not exist, it will be created.

        Args:
            zone_name (str): Name of the zone.
            zoneset_name (str): Name of the zoneset.
            vsan_id (str): VSAN ID.

        Returns:
            response (json): JSON response from the MDS switch.
        """

        logger.info(
            "Adding zone '%s' to zoneset '%s' in VSAN '%s'.\n",
            zone_name,
            zoneset_name,
            vsan_id,
        )

        # Construct the command to add zone to zoneset
        command = f"zoneset name {zoneset_name} vsan {vsan_id} ;member {zone_name}"
        logger.info("Constructed command to add zone to zoneset: '%s'.\n", command)

        # Send the POST request
        response = self.post_request(
            request_input=command, request_type=self.api_type_config
        )

        return response.json()

    # Method to configure zone on the MDS switch
    def configure_zone(self, zone_name: str, vsan_id: str):
        """
        Configure zone on the MDS switch in a specific VSAN.

        Args:
            zone_name (str): Name of the zone.
            vsan_id (str): VSAN ID.

        Returns:
            response (json): JSON response from the MDS switch.
        """

        logger.info(
            "Configuring zone '%s' in VSAN '%s'.",
            zone_name,
            vsan_id,
        )

        # Construct the command to configure zone
        command = f"zone name {zone_name} vsan {vsan_id}"
        logger.info("Constructed command to configure zone: '%s'.\n", command)

        # Send the POST request
        response = self.post_request(
            request_input=command, request_type=self.api_type_config
        )

        return response.json()

    # Method to configure a zone and add a member to it on the MDS switch
    def configure_zone_and_add_member(
        self,
        zone_name: str,
        vsan_id: str,
        wwpn: str = None,
        device_alias_name: str = None,
    ):
        """
        Add a member to a zone on the MDS switch in a specific VSAN.
        This method can add a member using either the WWPN or the device alias name.
        If both are provided, the device alias name will be used.
        This method also configures the zone if it does not exist.

        Args:
            zone_name (str): Name of the zone.
            vsan_id (str): VSAN ID.
            wwpn (str): WWPN of the member to be added.
            device_alias_name (str): Device alias name of the member to be added.
                If provided, it will be used instead of member_wwpn.
                If both are provided, device_alias_name will be used.
                If neither is provided, an error will be raised.

        Returns:
            response (json): JSON response from the MDS switch.
        """

        # Validate the member WWPN or device alias name
        if not wwpn and not device_alias_name:
            logger.error("Either member WWPN or device alias name must be provided.\n")
            sys.exit(1)

        # Use device alias name if provided
        if device_alias_name:

            logger.info(
                "Adding member with device alias '%s' to zone '%s' in VSAN '%s'.\n",
                device_alias_name,
                zone_name,
                vsan_id,
            )

            # Construct the command to configure zone and add a member with device alias to it
            command = f"zone name {zone_name} vsan {vsan_id} ;member device-alias {device_alias_name}"
            logger.info("Constructed command to add member to zone: '%s'\n", command)

        # Use member WWPN if device alias name is not provided
        elif wwpn:
            logger.info(
                "Adding member with WWPN '%s' to zone '%s' in VSAN '%s'.\n",
                wwpn,
                zone_name,
                vsan_id,
            )

            # Construct the command to configure zone and add a member WWPN to it
            command = f"zone name {zone_name} vsan {vsan_id} ;member pwwn {wwpn}"
            logger.info("Constructed command to add member to zone: '%s'.\n", command)

        # Send the POST request
        response = self.post_request(
            request_input=command, request_type=self.api_type_config
        )

        return response.json()

    # Method to fetch zone information from the MDS switch
    def fetch_zone_info(self, zone_name: str, vsan_id: str):
        """
        Fetch zone information from the MDS switch in a specific VSAN.

        Args:
            zone_name (str): Name of the zone.
            vsan_id (str): VSAN ID.

        Returns:
            response (json): JSON response from the MDS switch.
        """

        logger.info(
            "Fetching zone information for zone '%s' in VSAN '%s'.\n",
            zone_name,
            vsan_id,
        )

        # Construct the command to fetch zone information
        command = f"show zone name {zone_name} vsan {vsan_id}"
        logger.info("Constructed command to fetch zone information: %s.\n", command)

        # Send the POST request
        response = self.post_request(
            request_input=command, request_type=self.api_type_show
        )

        return response.json()
