#!/usr/bin/env python3

"""
This module defines the `IntersightClient` class for interacting with Cisco Intersight.

Author:
    Adrien LECHARNY - April 2025
"""

# Standard library imports
import datetime
import sys
import urllib3

# Third-party library imports
from intersight.model.vnic_fc_if import VnicFcIf
from intersight.model.mo_mo_ref import MoMoRef
from intersight.model.server_profile import ServerProfile
import intersight
from intersight.api import (
    organization_api,
    server_api,
    vnic_api,
)

# Local application imports
from base_logger import logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##############################################################################
#                          IntersightClient class                            #
##############################################################################


class IntersightClient:
    """
    Class to interact with Cisco Intersight API.

    This class provides various methods.

    Attributes:
        _intersight_key_id (str): The Intersight key ID.
        _intersight_secret_key_path (str): The path to the Intersight secret key.
        _intersight_url (str): The URL of the Cisco Intersight.
        _api_client (intersight.ApiClient): The Intersight API client.
    """

    def __init__(
        self,
        intersight_key_id: str,
        intersight_secret_key_path: str,
        intersight_url: str,
    ):
        """
        Initialize the IntersightClient class.

        Args:
            intersight_key_id (str): The Intersight key ID.
            intersight_secret_key_path (str): The path to the Intersight secret key.
            intersight_url (str): The URL of the Cisco Intersight."""

        logger.info(
            "Initializating IntersightClient instance with Cisco Intersight at URL '%s'\n",
            intersight_url,
        )

        # Check if the Intersight key ID is provided
        if not intersight_key_id:
            logger.error(
                "Intersight key ID is not provided. Please provide a valid Intersight key ID.\n"
            )
            sys.exit(1)
        # Check if the Intersight secret key path is provided
        if not intersight_secret_key_path:
            logger.error(
                "Intersight secret key path is not provided. Please provide a valid Intersight secret key path.\n"
            )
            sys.exit(1)
        # Check if the Intersight URL is provided
        if not intersight_url:
            logger.error(
                "Intersight URL is not provided. Please provide a valid Intersight URL.\n"
            )
            sys.exit(1)
        # Check if the Intersight URL is valid
        if not intersight_url.startswith("https://"):
            logger.error(
                "Intersight URL is not valid. Please provide a valid Intersight URL.\n"
            )
            sys.exit(1)
        self._intersight_key_id = intersight_key_id
        self._intersight_secret_key_path = intersight_secret_key_path
        self._intersight_url = intersight_url

        self._api_client = self.authenticate_and_assign_intersight_api_client()

        logger.info(
            "IntersightClient instance was successfully initialized with Cisco Intersight at URL '%s'\n",
            intersight_url,
        )

    # Method to authenticate to Intersight and assign Intersight API client to IntersightClient.
    def authenticate_and_assign_intersight_api_client(self):
        """
        Authenticates to Intersight and assigns Intersight API client to IntersightClient instance.

        This method generates Intersight API client for authentication to Intersight. It sets up the necessary configuration
        including Intersight URL, signing information, signing scheme, signing algorithm, signed headers, and signature validity.
        It also sets the default header for the API client.

        Args:
            None

        Returns:
            None
        """
        logger.info(
            "Generating Intersight API client for authentication to Intersight\n"
        )

        intersight_key_id = self._intersight_key_id

        configuration = intersight.Configuration(
            host=self._intersight_url,
            signing_info=intersight.signing.HttpSigningConfiguration(
                key_id=intersight_key_id,
                private_key_path=self._intersight_secret_key_path,
                # For OpenAPI v2
                # signing_scheme=intersight.signing.SCHEME_RSA_SHA256,
                # For OpenAPI v3
                signing_scheme=intersight.signing.SCHEME_HS2019,
                # For OpenAPI v2
                # signing_algorithm=intersight.signing.ALGORITHM_RSASSA_PKCS1v15,
                # For OpenAPI v3
                signing_algorithm=intersight.signing.ALGORITHM_ECDSA_MODE_FIPS_186_3,
                signed_headers=[
                    intersight.signing.HEADER_REQUEST_TARGET,
                    intersight.signing.HEADER_CREATED,
                    intersight.signing.HEADER_EXPIRES,
                    intersight.signing.HEADER_HOST,
                    intersight.signing.HEADER_DATE,
                    intersight.signing.HEADER_DIGEST,
                    "Content-Type",
                    "User-Agent",
                ],
                signature_max_validity=datetime.timedelta(minutes=5),
            ),
        )

        configuration.discard_unknown_keys = True
        configuration.disabled_client_side_validations = "minimum"
        configuration.verify_ssl = False
        api_client = intersight.ApiClient(configuration)
        api_client.set_default_header("Content-Type", "application/json")

        logger.info(
            "Authentication was successfull and Intersight API client was successfully generated and assigned to IntersightClient\n"
        )

        return api_client

    # Method to fetch Server Profile moid filtered by Server Profile name and Organization moid
    def fetch_server_profile_moid_from_server_profile_name_and_organization_moid(
        self, server_profile_name: str, organization_moid: str
    ):
        """
        Fetches a Server Profile moid filtered by the given Server Profile name and Organization moid.

        Args:
            server_profile_name (str): The name of the Server Profile.
            organization_moid (str): The moid of the Organization.

        Returns:
            server_profile_moid (str): The Server Profile moid.

        Raises:
            intersight.ApiException: If an error occurs while retrieving the Server Profile.
        """
        logger.info(
            "Fetching Server Profile moid filtered by Server Profile name '%s' and Organization moid `%s`\n",
            server_profile_name,
            organization_moid,
        )

        api_instance = server_api.ServerApi(self._api_client)

        # Create filter.
        filter_str = f"Name eq '{server_profile_name}' and Organization.Moid eq '{organization_moid}'"

        # Read a 'server.Profile' resource with filter.
        try:
            server_profile_result = api_instance.get_server_profile_list(
                filter=filter_str
            )

        except intersight.ApiException as exception:
            logger.warning(
                "Exception when calling ServerApi->get_server_profile_list: '%s'\n",
                exception,
            )
            sys.exit(1)

        if server_profile_result.results:
            server_profile_moid = server_profile_result.results[0].moid
            logger.info(
                "Moid of the Server Profile name '%s' is '%s'\n",
                server_profile_name,
                server_profile_moid,
            )
        else:
            logger.error(
                "Server Profile with name '%s' with Organization moid `%s` not found in Intersight\n",
                server_profile_name,
                organization_moid,
            )
            sys.exit(1)

        return server_profile_moid

    # Method  to fetch Organization moid filtered by Organization name
    def fetch_organization_moid_from_organization_name(self, organization_name: str):
        """
        Fetches an Organization moid filtered by the given Organization name.

        Args:
            organization_name (str): The name of the Organization.

        Returns:
            organization_moid (str): The moid of the Organization.

        Raises:
            intersight.ApiException: If an error occurs while retrieving the Organization.
        """
        logger.info(
            "Fetching Organization moid filtered by Organization name '%s'\n",
            organization_name,
        )

        api_instance = organization_api.OrganizationApi(self._api_client)

        # Create filter.
        filter_str = f"Name eq '{organization_name}'"

        # Read a 'organization.Organization' resource with filter.
        try:
            organization_result = api_instance.get_organization_organization_list(
                filter=filter_str
            )

        except intersight.ApiException as exception:
            logger.warning(
                "Exception when calling OrganizationApi->get_organization_organization_list: '%s'\n",
                exception,
            )
            sys.exit(1)

        if organization_result.results:
            organization_moid = organization_result.results[0].moid
            logger.info(
                "Moid of the Organization name '%s' is '%s'\n",
                organization_name,
                organization_moid,
            )
        else:
            logger.error(
                "Organization with name '%s' not found in Intersight\n",
                organization_name,
            )
            sys.exit(1)

        return organization_moid

    # Method to fetch and create list of vHBAs attached to a Server Profile filtered by Server Profile moid
    def fetch_vhba_from_server_profile_moid(
        self,
        server_profile_moid: str,
    ):
        """
        Fetches vHBAs attached to a Server Profile filtered by the given Server Profile moid.

        Args:
            server_profile_moid (str): The moid of the Server Profile.

        Returns:
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

        Raises:
            intersight.ApiException: If an error occurs while retrieving the vHBA WWPN.
        """
        logger.info(
            "Fetching vHBAs attached to a Server Profile filtered by Server Profile moid '%s'\n",
            server_profile_moid,
        )

        api_instance = vnic_api.VnicApi(self._api_client)

        # Create filter.
        filter_str = f"Profile.Moid eq '{server_profile_moid}'"

        # Read a 'vnic.VnicFcIf' resource with filter.
        try:
            vnic_fc_if_result = api_instance.get_vnic_fc_if_list(filter=filter_str)

        except intersight.ApiException as exception:
            logger.warning(
                "Exception when calling VnicApi->get_vnic_fc_if_list: '%s'\n",
                exception,
            )
            sys.exit(1)

        if vnic_fc_if_result.results:
            vhba_list = []
            for vnic_fc_if in vnic_fc_if_result.results:
                vhba_list.append(
                    {
                        "vhba_wwpn": vnic_fc_if.wwpn,
                        "vhba_name": vnic_fc_if.name,
                        "vhba_fabric": vnic_fc_if.placement.switch_id,
                    }
                )
            logger.info(
                "List of vHBAs attached to Server Profile with moid '%s' is '%s'\n",
                server_profile_moid,
                vhba_list,
            )
        else:
            logger.error(
                "vHBAs not found in Intersight for Server Profile with moid '%s'\n",
                server_profile_moid,
            )
            sys.exit(1)

        return vhba_list

    # Method to fetch and create Organization reference objects
    def fetch_and_create_organization_reference_object_from_organization_name(
        self, organization_name: str
    ):
        """
        Creates an Organization reference object from the given organization name.

        Args:
            organization_name (str): The name of the organization.

        Returns:
            organization_reference (MoMoRef): The created Organization reference.

        Raises:
            intersight.ApiException: If an error occurs while retrieving the organization.

        """
        logger.info(
            "Creating Organization reference object from Organization name %s\n",
            organization_name,
        )

        api_instance = organization_api.OrganizationApi(self._api_client)

        # Create filter.
        filter_str = f"Name eq {organization_name}"

        # Read a 'organization.Organization' resource with filter.
        try:
            organization_result = api_instance.get_organization_organization_list(
                filter=filter_str
            )

        except intersight.ApiException as exception:
            logger.warning(
                "Exception when calling OrganizationApi->get_organization_organization_list: %s\n",
                exception,
            )
            sys.exit(1)

        if organization_result.results:
            organization_moid = organization_result.results[0].moid
            logger.info(
                "Moid of the organization name %s is %s\n",
                organization_name,
                organization_moid,
            )

            # Create 'Organization' reference object.
            organization_reference = MoMoRef(
                object_type="organization.Organization",
                moid=organization_moid,
            )

            logger.info(
                "Organization reference object from Organization name %s was successfully created\n",
                organization_name,
            )

        else:
            logger.error(
                "Organization with name %s not found in Intersight\n",
                organization_name,
            )
            sys.exit(1)

        return organization_reference
