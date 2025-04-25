#!/usr/bin/env python3

"""
This module allows to quickly test the ZoneBridgeClient class and its methods.
It uses environment variables and user-defined variables to configure the Intersight and MDS clients.

Author:
    Adrien LECHARNY - April 2025
"""

# Standard library imports
import os
from dotenv import load_dotenv

# Local application imports
from intersight_client_class import IntersightClient
from mds_client_class import MdsClient
from zone_bridge_client_class import ZoneBridgeClient

##############################################################################
#                             Env Variables                                  #
##############################################################################

# Load environment variables from .env file
# All sensitive information should be stored in a .env file and not hardcoded in the script.
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


##############################################################################
#                             User Variables                                 #
##############################################################################

# Server Profile in Intersight
SERVER_PROFILE_NAME = "new-server-profile"
ORGANIZATION_NAME = "default"

# Zoning - Fabric A
ZONESET_A = "zoneset-demo-a"
ZONE_A = SERVER_PROFILE_NAME
VSAN_A = "100"

# Zoning - Fabric B
ZONESET_B = "zoneset-demo-b"
ZONE_B = SERVER_PROFILE_NAME
VSAN_B = "200"


###############################################################################
#                                   Main                                      #
###############################################################################

if __name__ == "__main__":

    # Initialize clients
    intersight_client = IntersightClient(
        intersight_key_id=INTERSIGHT_KEY_ID,
        intersight_secret_key_path=INTERSIGHT_SECRET_KEY_PATH,
        intersight_url=INTERSIGHT_URL,
    )

    mds_client_a = MdsClient(
        mds_ip_address=MDS_IP_ADDRESS_A,
        mds_username=MDS_USERNAME_A,
        mds_password=MDS_PASSWORD_A,
    )

    mds_client_b = MdsClient(
        mds_ip_address=MDS_IP_ADDRESS_B,
        mds_username=MDS_USERNAME_B,
        mds_password=MDS_PASSWORD_B,
    )

    zone_bridge_client = ZoneBridgeClient(
        intersight_client=intersight_client,
        mds_client_a=mds_client_a,
        mds_client_b=mds_client_b,
    )

    # Configure device-aliases and zoning in MDS based on Intersight Server Profile vHBAs
    zone_bridge_client.configure_intersight_mds_zones(
        server_profile_name=SERVER_PROFILE_NAME,
        organization_name=ORGANIZATION_NAME,
        zoneset_name_a=ZONESET_A,
        zone_name_a=ZONE_A,
        vsan_id_a=VSAN_A,
        zoneset_name_b=ZONESET_B,
        zone_name_b=ZONE_B,
        vsan_id_b=VSAN_B,
        flag_configure_device_aliases=True,
        flag_add_zones_to_zonesets=True,
        flag_activate_zonesets=True,
    )
