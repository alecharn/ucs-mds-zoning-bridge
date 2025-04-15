#!/usr/bin/env python3

"""
This module defines the ZoneBridgeClient class to link the Intersight and MDS clients.

Author:
    Adrien LECHARNY - April 2025
"""

# Standard library imports
import sys

# Local application imports
from base_logger import logger


##############################################################################
#                          ZoneBridgeClient class                            #
##############################################################################


class ZoneBridgeClient:
    """
    Class to link the Intersight and MDS clients.

    This class provides various methods to interact with both clients.
    """

    # Class variables
    def __init__(self, intersight_client, mds_client_a, mds_client_b):
        """
        Initialize the ZoneBridgeClient class.

        Args:
            intersight_client (IntersightClient): Instance of IntersightClient.
            mds_client_a (MdsClient): Instance of MdsClient for Fabric A.
            mds_client_b (MdsClient): Instance of MdsClient for Fabric B.
        """

        self.intersight_client = intersight_client
        self.mds_client_a = mds_client_a
        self.mds_client_b = mds_client_b

    # Method to activate zonesets on each MDS of Fabric A and B
    def activate_zonesets(
        self, zoneset_name_a: str, vsan_id_a: str, zoneset_name_b: str, vsan_id_b: str
    ):
        """
        Activate zonesets on each MDS of Fabric A and B.
        This method activates the zonesets in the respective MDS clients.
        It is assumed that the zonesets have already been created and configured.

        Args:
            zoneset_name_a (str): Name of the zoneset in Fabric A.
            vsan_id_a (str): VSAN ID for the zoneset in Fabric A.
            zoneset_name_b (str): Name of the zoneset in Fabric B.
            vsan_id_b (str): VSAN ID for the zoneset in Fabric B.

        Returns:
            None
        """

        # Activate the zoneset in Fabric A
        logger.info(
            "Activating zoneset '%s' of vsan `%s` in MDS '%s' (Fabric A)\n",
            zoneset_name_a,
            vsan_id_a,
            self.mds_client_a.ip_address,
        )
        self.mds_client_a.activate_zoneset(
            zoneset_name=zoneset_name_a, vsan_id=vsan_id_a
        )

        # Activate the zoneset in Fabric B
        logger.info(
            "Activating zoneset '%s' of vsan `%s` in MDS '%s' (Fabric B)\n",
            zoneset_name_b,
            vsan_id_b,
            self.mds_client_b.ip_address,
        )
        self.mds_client_b.activate_zoneset(
            zoneset_name=zoneset_name_b, vsan_id=vsan_id_b
        )

    # Method to fetch vHBAs attached to an Intersight Server Profile, and configure them as device aliases on each MDS of Fabric A and B
    def add_device_aliases_from_server_profile_name_and_vhba(
        self, server_profile_name: str, vhba_list: list
    ):
        """
        Fetch vHBAs attached to an Intersight Server Profile, and configure them as device aliases on each MDS of Fabric A and B.
        This method creates device aliases based on the Server Profile name, vHBA name and Fabric.

        Args:
            server_profile_name (str): Name of the Server Profile in Intersight.
            vhba_list (list): A list of dictionaries containing vHBA WWPN, name and Fabric information.
            Each dictionary contains the keys 'vhba_wwpn', 'vhba_name' and 'vhba_fabric'.
            Example:
                [
                    {
                        "vhba_wwpn": "20:00:00:00:00:00:00:01",
                        "vhba_name": "vHBA0",
                        "vhba_fabric": "A"
                    },
                    {
                        "vhba_wwpn": "20:00:00:00:00:00:00:02",
                        "vhba_name": "vHBA1",
                        "vhba_fabric": "B"
                    }
                ]

        Returns:
            None
        """

        # Iterate over the VHBA list
        for vhba in vhba_list:

            # Create device alias from server profile name, vHBA name and Fabric
            device_alias = (
                f"{server_profile_name}-{vhba['vhba_fabric']}-{vhba['vhba_name']}"
            )

            # Check if the vHBA is in Fabric A or B
            if vhba["vhba_fabric"] == "A":

                logger.info(
                    "Adding device alias '%s' with WWPN '%s' to MDS '%s' (Fabric A)\n",
                    device_alias,
                    vhba["vhba_wwpn"],
                    self.mds_client_a.ip_address,
                )
                # Add the device alias in Fabric A
                self.mds_client_a.add_device_alias(
                    device_alias_name=device_alias,
                    wwpn=vhba["vhba_wwpn"],
                )

            elif vhba["vhba_fabric"] == "B":
                logger.info(
                    "Adding device alias '%s' with WWPN '%s' to MDS '%s' (Fabric B)\n",
                    device_alias,
                    vhba["vhba_wwpn"],
                    self.mds_client_b.ip_address,
                )
                # Add the device alias in Fabric B
                self.mds_client_b.add_device_alias(
                    device_alias_name=device_alias,
                    wwpn=vhba["vhba_wwpn"],
                )

            else:
                logger.error(
                    "Unknown fabric type '%s' for vHBA '%s'",
                    vhba["fabric"],
                    vhba["name"],
                )
                sys.exit(1)

    # Method to add zones in zonesets on each MDS of Fabric A and B
    def add_zones_to_zonesets(
        self,
        zoneset_name_a: str,
        zone_name_a: str,
        vsan_id_a: str,
        zoneset_name_b: str,
        zone_name_b: str,
        vsan_id_b: str,
    ):
        """
        Add zones in zonesets on each MDS of Fabric A and B.
        This method adds the specified zones to the respective zonesets in the MDS clients.
        It is assumed that the zones have already been created and configured.

        Args:
            zoneset_name_a (str): Name of the zoneset in Fabric A.
            zone_name_a (str): Name of the zone to be added in Fabric A.
            vsan_id_a (str): VSAN ID for the zone configuration in Fabric A.
            zoneset_name_b (str): Name of the zoneset in Fabric B.
            zone_name_b (str): Name of the zone to be added in Fabric B.
            vsan_id_b (str): VSAN ID for the zone configuration in Fabric B.

        Returns:
            None
        """

        # Add the zone to the zoneset in Fabric A
        logger.info(
            "Adding zone '%s' of vsan `%s` to zoneset '%s' in MDS '%s' (Fabric A)\n",
            zone_name_a,
            vsan_id_a,
            zoneset_name_a,
            self.mds_client_a.ip_address,
        )
        self.mds_client_a.add_zone_to_zoneset(
            zone_name=zone_name_a,
            zoneset_name=zoneset_name_a,
            vsan_id=vsan_id_a,
        )

        # Add the zone to the zoneset in Fabric B
        logger.info(
            "Adding zone '%s' of vsan `%s` to zoneset '%s' in MDS '%s' (Fabric B)\n",
            zone_name_b,
            vsan_id_b,
            zoneset_name_b,
            self.mds_client_b.ip_address,
        )
        self.mds_client_b.add_zone_to_zoneset(
            zone_name=zone_name_b,
            zoneset_name=zoneset_name_b,
            vsan_id=vsan_id_b,
        )

    # Method to fetch WWPNs attached to a Server Profile in Intersight, optionnaly configure device aliases and add them as members of a zone on each MDS of Fabric A and B
    def configure_intersight_mds_zones(
        self,
        server_profile_name: str,
        organization_name: str,
        zone_name_a: str,
        vsan_id_a: str,
        zone_name_b: str,
        vsan_id_b: str,
        zoneset_name_a: str = None,
        zoneset_name_b: str = None,
        flag_configure_device_aliases: bool = True,
        flag_add_zones_to_zonesets: bool = True,
        flag_activate_zonesets: bool = True,
    ):
        """
        Fetch vHBAs attached to an Intersight Server Profile, optionnaly configure device aliases, and add them as members of a zone on each MDS of Fabric A and B.

        This method is used to configure zones in MDS based on the vHBAs attached to a Server Profile in Intersight.
        It fetches the vHBA information from Intersight and configures device aliases on MDS (if the flag is set to true).
        It also adds the vHBA WWPNs or device aliases as members of the specified zones in MDS.

        Args:
            server_profile_name (str): Name of the Server Profile in Intersight.
            organization_name (str): Name of the organization in Intersight.
            zoneset_name_a (str): Name of the zoneset in MDS.
            zone_name_a (str): Name of the zone to be configured in MDS.
            vsan_id_a (str): VSAN ID for the zone configuration.
            zoneset_name_b (str): Name of the zoneset in MDS.
            zone_name_b (str): Name of the zone to be configured in MDS.
            vsan_id_b (str): VSAN ID for the zone configuration.
            flag_configure_device_aliases (bool): Flag to configure device aliases on MDS.
                Default is True.
                If set to True, device aliases will be configured and will be used to add member in zone.
                If set to False, WWPNs will be added directly to the zones.
            flag_add_zones_to_zonesets (bool): Flag to add zones to zonesets.
                Default is True.
                If set to True, zones will be added to the zonesets.
                If set to False, zones will not be added to the zonesets.
            flag_activate_zonesets (bool): Flag to activate zonesets.
                Default is True.
                If set to True, zonesets will be activated.
                If set to False, zonesets will not be activated.

        Returns:
            None
        """

        # Fetch the organization moid from Intersight
        organization_moid = (
            self.intersight_client.fetch_organization_moid_from_organization_name(
                organization_name=organization_name,
            )
        )

        # Fetch the server profile moid from Intersight
        server_profile = self.intersight_client.fetch_server_profile_moid_from_server_profile_name_and_organization_moid(
            server_profile_name=server_profile_name,
            organization_moid=organization_moid,
        )

        # Fetch the VHBA list attached to the server profile
        vhbas_list = self.intersight_client.fetch_vhba_from_server_profile_moid(
            server_profile,
        )

        # Iterate over the VHBA list
        for vhba in vhbas_list:

            # Check if flag to configure device aliases is set to True
            # If flag is set to True, device alias is used for zoning
            if flag_configure_device_aliases:
                device_alias_name = (
                    f"{server_profile_name}-{vhba['vhba_fabric']}-{vhba['vhba_name']}"
                )

                # Add the device alias in MDS
                logger.info(
                    "Adding device alias '%s' with WWPN '%s' to MDS '%s' (Fabric %s)\n",
                    device_alias_name,
                    vhba["vhba_wwpn"],
                    (
                        self.mds_client_a.ip_address
                        if vhba["vhba_fabric"] == "A"
                        else self.mds_client_b.ip_address
                    ),
                    vhba["vhba_fabric"],
                )
                if vhba["vhba_fabric"] == "A":
                    self.mds_client_a.add_device_alias(
                        device_alias_name=device_alias_name,
                        wwpn=vhba["vhba_wwpn"],
                    )
                elif vhba["vhba_fabric"] == "B":
                    self.mds_client_b.add_device_alias(
                        device_alias_name=device_alias_name,
                        wwpn=vhba["vhba_wwpn"],
                    )
                else:
                    logger.error(
                        "Unknown fabric type '%s' for vHBA '%s'",
                        vhba["fabric"],
                        vhba["name"],
                    )
                    sys.exit(1)

            # If flag is set to False, use the WWPN directly for zoning
            # and do not configure device aliases
            elif flag_configure_device_aliases is False:
                device_alias_name = None
                logger.info(
                    "Skipping device alias creation for vHBA '%s' with WWPN '%s'\n",
                    vhba["vhba_name"],
                    vhba["vhba_wwpn"],
                )
                logger.info(
                    "Using WWPN '%s' directly for vHBA '%s' to configue zone member\n",
                    vhba["vhba_wwpn"],
                    vhba["vhba_name"],
                )

            else:
                logger.error(
                    "Unknown flag value '%s' for device alias configuration",
                    flag_configure_device_aliases,
                )
                sys.exit(1)

            # Check if the vHBA is in Fabric A or B
            if vhba["vhba_fabric"] == "A":
                logger.info(
                    "Adding vHBA '%s' to zone '%s' in vsan '%s' of MDS '%s' (Fabric A)\n",
                    vhba["vhba_wwpn"],
                    zone_name_a,
                    vsan_id_a,
                    self.mds_client_a.ip_address,
                )

                # Add the member to the zone in Fabric A
                self.mds_client_a.configure_zone_and_add_member(
                    zone_name=zone_name_a,
                    vsan_id=vsan_id_a,
                    wwpn=vhba["vhba_wwpn"],
                    device_alias_name=device_alias_name,
                )

            elif vhba["vhba_fabric"] == "B":
                logger.info(
                    "Adding vHBA '%s' to zone '%s' in vsan '%s' of MDS '%s' (Fabric B)\n",
                    vhba["vhba_wwpn"],
                    zone_name_b,
                    vsan_id_b,
                    self.mds_client_b.ip_address,
                )
                # Add the member to the zone in Fabric B
                self.mds_client_b.configure_zone_and_add_member(
                    zone_name=zone_name_b,
                    vsan_id=vsan_id_b,
                    wwpn=vhba["vhba_wwpn"],
                    device_alias_name=device_alias_name,
                )

            else:
                logger.error(
                    "Unknown fabric type '%s' for vHBA '%s'",
                    vhba["fabric"],
                    vhba["name"],
                )
                sys.exit(1)

        # Add zones to zonesets if the flag is set to True
        if flag_add_zones_to_zonesets:
            logger.info(
                "Adding zones to zonesets in MDS\n",
            )

            # Check that zoneset names are provided
            if zoneset_name_a is None or zoneset_name_b is None:
                logger.error(
                    "Zoneset names are required to add zones to zonesets in MDS\n"
                )
                sys.exit(1)

            # Add the zone to the zoneset in Fabric A
            logger.info(
                "Adding zone '%s' of vsan `%s` to zoneset '%s' in MDS '%s' (Fabric A)\n",
                zone_name_a,
                vsan_id_a,
                zoneset_name_a,
                self.mds_client_a.ip_address,
            )
            self.mds_client_a.add_zone_to_zoneset(
                zone_name=zone_name_a,
                zoneset_name=zoneset_name_a,
                vsan_id=vsan_id_a,
            )

            # Add the zone to the zoneset in Fabric B
            logger.info(
                "Adding zone '%s' of vsan `%s` to zoneset '%s' in MDS '%s' (Fabric B)\n",
                zone_name_b,
                vsan_id_b,
                zoneset_name_b,
                self.mds_client_b.ip_address,
            )
            self.mds_client_b.add_zone_to_zoneset(
                zone_name=zone_name_b,
                zoneset_name=zoneset_name_b,
                vsan_id=vsan_id_b,
            )

        else:
            logger.info("Skipping adding zones to zonesets in MDS\n")

        # Activate zonesets if the flag is set to True
        if flag_activate_zonesets:

            # Check that zoneset names are provided
            if zoneset_name_a is None or zoneset_name_b is None:
                logger.error(
                    "Zoneset names are required to add zones to zonesets in MDS\n"
                )
                sys.exit(1)

            logger.info(
                "Activating zonesets in MDS\n",
            )

            # Activate the zoneset in Fabric A
            logger.info(
                "Activating zoneset '%s' of vsan `%s` in MDS '%s' (Fabric A)\n",
                zoneset_name_a,
                vsan_id_a,
                self.mds_client_a.ip_address,
            )
            self.mds_client_a.activate_zoneset(
                zoneset_name=zoneset_name_a, vsan_id=vsan_id_a
            )

            # Activate the zoneset in Fabric B
            logger.info(
                "Activating zoneset '%s' of vsan `%s` in MDS '%s' (Fabric B)\n",
                zoneset_name_b,
                vsan_id_b,
                self.mds_client_b.ip_address,
            )
            self.mds_client_b.activate_zoneset(
                zoneset_name=zoneset_name_b, vsan_id=vsan_id_b
            )

        else:
            logger.info("Skipping activating zonesets in MDS\n")
