#!/usr/bin/env python3

"""
This module defines a CLI for managing zoning using the ZoneBridgeClient.

Author:
    Adrien LECHARNY - April 2025
"""

# Standard library imports
import os
from dotenv import load_dotenv

# Third-party library imports
import fire

# Local application imports
from intersight_client_class import IntersightClient
from mds_client_class import MdsClient
from zone_bridge_client_class import ZoneBridgeClient

##############################################################################
#                             Env Variables                                  #
##############################################################################

# Load environment variables from .env file
load_dotenv()

# .ENV.MAIN
MAIN_ENV_PATH = os.getenv("MAIN_ENV_PATH")
load_dotenv(MAIN_ENV_PATH)

# Intersight API credentials
INTERSIGHT_KEY_ID = os.getenv("INTERSIGHT_KEY_ID")
INTERSIGHT_SECRET_KEY_PATH = os.getenv("INTERSIGHT_SECRET_KEY_PATH")
INTERSIGHT_URL = "https://intersight.com"

# MDS credentials - Fabric A
MDS_IP_ADDRESS_A = os.getenv("MDS_IP_ADDRESS_A")
MDS_USERNAME_A = os.getenv("MDS_USERNAME_A")
MDS_PASSWORD_A = os.getenv("MDS_PASSWORD_A")

# MDS credentials - Fabric B
MDS_IP_ADDRESS_B = os.getenv("MDS_IP_ADDRESS_B")
MDS_USERNAME_B = os.getenv("MDS_USERNAME_B")
MDS_PASSWORD_B = os.getenv("MDS_PASSWORD_B")


###############################################################################
#                                   Main                                      #
###############################################################################


if __name__ == "__main__":

    # Initialize Intersight Client
    intersight_client = IntersightClient(
        INTERSIGHT_KEY_ID, INTERSIGHT_SECRET_KEY_PATH, INTERSIGHT_URL
    )

    # Initialize MDS Clients for Fabric A and B
    mds_client_a = MdsClient(MDS_IP_ADDRESS_A, MDS_USERNAME_A, MDS_PASSWORD_A)
    mds_client_b = MdsClient(MDS_IP_ADDRESS_B, MDS_USERNAME_B, MDS_PASSWORD_B)

    # Initialize ZoneBridgeClient
    zone_bridge_client = ZoneBridgeClient(intersight_client, mds_client_a, mds_client_b)

    # Start the CLI
    fire.Fire(zone_bridge_client)
