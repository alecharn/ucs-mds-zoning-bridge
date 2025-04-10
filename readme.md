# ucs-mds-zoning-bridge

ucs-mds-zoning-bridge is a tool designed to simplify and automate the process of managing zoning configurations between Cisco UCS and MDS switches. This tool bridges the gap between UCS Server Profiles vHBAs configured in Intersight and MDS zoning, ensuring seamless integration and efficient management.

## Features

- **Automated Device Aliases**: Automatically configures devices aliases from UCS Server Profiles' vHBAs defined in Intersight.
- **Automated Zoning**: Automatically configures zoning from UCS Server Profiles' vHBAs defined in Intersight.
- **CLI interaction**: CLI is automatically generated through the [Google Python Fire project](https://github.com/google/python-fire).

## Prerequisites

Before using this tool, ensure the following:

- Python 3.8 or later is installed.
- Access to Cisco Intersight with appropriate Intersight API keys. Refer to the [Intersight API Key Generation Guide](https://intersight.com/apidocs/introduction/security/) for detailed instructions.
- Access to Cisco MDS switches with appropriate credentials. NX-API feature must be turned on. Refer to the [Cisco MDS 9000 Series Programmability Guide](https://www.cisco.com/c/en/us/td/docs/dcn/mds9000/sw/9x/programmability/cisco-mds-9000-nx-os-programmability-guide-9x/nx_api.html) for detailed instructions. 
- Required Python libraries installed (see [Installation](#installation) section).
- Network connectivity between the system running the tool and Intersight/MDS devices.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/ucs-mds-zoning-bridge.git
    cd ucs-mds-zoning-bridge
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up the tool by modifying the environment variables in the `zone_bridge_fire.py` file to give access to Intersight API keys and MDS credentials. Alternatively, you can directly define the Intersight API keys and MDS credentials as variables within the script (this approach is not recommended for many reasons).

## Usage

### Configure vHBAs device-aliases, configure zoning with vHBAs device-aliases, add zones to zoneset, then activate zoneset

To synchronize UCS Server Profile vHBAs with MDS zones and zonesets based on vHBAs device-aliases:

```bash
python zone_bridge_fire.py configure_intersight_mds_zones --server_profile_name=new-server-profile --organization_name=demo --zone_name_a=new-server-profile-a --vsan_id_a=100 --zone_name_b=new-server-profile-b --vsan_id_b=200 --zoneset_name_a=zoneset-demo-a --zoneset_name_b=zoneset-demo-b --flag_configure_device_aliases=true --flag_add_zones_to_zonesets=true --flag_activate_zonesets=true
```

### Configure zoning with vHBAs WWPNs, then add zones to zoneset, finally activate zoneset

To synchronize UCS Server Profile vHBAs with MDS zones and zonesets based on vHBAs WWPNs:

```bash
python zone_bridge_fire.py configure_intersight_mds_zones --server_profile_name=new-server-profile --organization_name=demo --zone_name_a=new-server-profile-a --vsan_id_a=100 --zone_name_b=new-server-profile-b --vsan_id_b=200 --zoneset_name_a=zoneset-demo-a --zoneset_name_b=zoneset-demo-b --flag_configure_device_aliases=false --flag_add_zones_to_zonesets=true --flag_activate_zonesets=true
```

### Configure zoning with vHBAs WWPNs, do not add zones to zoneset, do not activate zoneset

To only configure MDS zones with UCS Server Profile vHBAs WWPNs:

```bash
python zone_bridge_fire.py configure_intersight_mds_zones --server_profile_name=new-server-profile --organization_name=demo --zone_name_a=new-server-profile-a --vsan_id_a=100 --zone_name_b=new-server-profile-b --vsan_id_b=200 --zoneset_name_a=zoneset-demo-a --zoneset_name_b=zoneset-demo-b --flag_configure_device_aliases=false --flag_add_zones_to_zonesets=false --flag_activate_zonesets=false
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.
