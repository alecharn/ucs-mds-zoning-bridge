# ucs-mds-zoning-bridge

ucs-mds-zoning-bridge is a tool designed to simplify and automate the process of managing zoning configurations between Cisco UCS and MDS switches. This tool bridges the gap between UCS Server Profiles vHBAs configured in Intersight and MDS zoning, ensuring seamless integration and efficient management.

## Features

- **Automated Device Aliases**: Automatically configures device-aliases from UCS Server Profiles' vHBAs defined in Intersight.
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

### CLI Usage

The CLI provides the following options for configuring zoning:

```bash
python zone_bridge_fire.py configure_intersight_mds_zones [OPTIONS]
```

#### Options:

- `--server_profile_name`: (Required) Name of the UCS Server Profile to synchronize.
- `--organization_name`: (Required) Name of the organization in Intersight where the Server Profile is attached.
- `--zone_name_a`: (Required) Name of the zone for MDS A.
- `--vsan_id_a`: (Required) VSAN ID for MDS A.
- `--zone_name_b`: (Required) Name of the zone for MDS B.
- `--vsan_id_b`: (Required) VSAN ID for MDS B.
- `--zoneset_name_a`: (Required if `flag_add_zones_to_zonesets` is set to `true`) Name of the zoneset for MDS A. Default is `None`.
- `--zoneset_name_b`: (Required if `flag_add_zones_to_zonesets` is set to `true`) Name of the zoneset for MDS B. Default is `None`.
- `--flag_configure_device_aliases`: (Optional) Boolean flag to configure device aliases. Default is `true`.
- `--flag_add_zones_to_zonesets`: (Optional) Boolean flag to add zones to zonesets. Default is `true`.
- `--flag_activate_zonesets`: (Optional) Boolean flag to activate zonesets. Default is `true`.

### Device-Aliases Considerations

If `flag_configure_device_aliases` is set to `true`, device-alias is automatically created for the vHBAs WWPNs on each MDS, and has the following structure: `{server_profile_name}-{fabric}-{vhba_name}`

For example, if the Server Profile in Intersight is named `ucs-sp-1`, has two vHBAs with names `vhba0` attached to Fabric A (`WWPN 20:00:00:00:00:00:00:01`) and `vhba1` attached to Fabric B (`WWPN 20:00:00:00:00:00:00:02`), the device-aliases would be:
- On MDS A : `device-alias name ucs-sp-1-A-vhba0 pwwn 20:00:00:00:00:00:00:01`
- On MDS B : `device-alias name ucs-sp-1-B-vhba1 pwwn 20:00:00:00:00:00:00:02`

When `flag_configure_device_aliases` is set to `true`, device-aliases are used to add members in MDS zones instead of directly using the WWPNs of vHBAs. For example, if using zone `zone-demo-a` in `vsan 100` of MDS A, following configuration would be pushed to MDS A :
```bash
zone name zone-demo-a vsan 100
    member device-alias ucs-sp-1-A-vhba0
```

When `flag_configure_device_aliases` is set to `false`, WWPNs of vHBAs are used to add members in MDS zones. For example, if using zone `zone-demo-a` in `vsan 100` of MDS A, following configuration would be pushed to MDS A :
```bash
zone name zone-demo-a vsan 100
    member pwwn 20:00:00:00:00:00:00:01
```

### Usage Examples:

#### Example 1

Fetch UCS Server Profile and its vHBAs WWPNs, create device-aliases, add the device-aliases as member of MDS zones, add zones to zonesets and activate zonesets:

```bash
python zone_bridge_fire.py configure_intersight_mds_zones \
    --server_profile_name=ucs-sp-1 \
    --organization_name=demo \
    --zone_name_a=zone-demo-a \
    --vsan_id_a=100 \
    --zone_name_b=zone-demo-b \
    --vsan_id_b=200 \
    --zoneset_name_a=zoneset-demo-a \
    --zoneset_name_b=zoneset-demo-b \
    --flag_configure_device_aliases=true \
    --flag_add_zones_to_zonesets=true \
    --flag_activate_zonesets=true
```

#### Example 2

Fetch UCS Server Profile and its vHBAs WWPNs, skip device-aliases creation, add the vHBAs WWPNs as member of MDS zones, add zones to zonesets and activate zonesets:

```bash
python zone_bridge_fire.py configure_intersight_mds_zones \
    --server_profile_name=ucs-sp-1 \
    --organization_name=demo \
    --zone_name_a=zone-demo-a \
    --vsan_id_a=100 \
    --zone_name_b=zone-demo-b \
    --vsan_id_b=200 \
    --zoneset_name_a=zoneset-demo-a \
    --zoneset_name_b=zoneset-demo-b \
    --flag_configure_device_aliases=false \
    --flag_add_zones_to_zonesets=true \
    --flag_activate_zonesets=true
```

#### Example 3

Fetch UCS Server Profile and its vHBAs WWPNs, skip device-aliases creation, add the vHBAs WWPNs as member of MDS zones, skip adding zones to zonesets and skip zonesets activation:

```bash
python zone_bridge_fire.py configure_intersight_mds_zones \
    --server_profile_name=ucs-sp-1 \
    --organization_name=demo \
    --zone_name_a=zone-demo-a \
    --vsan_id_a=100 \
    --zone_name_b=zone-demo-b \
    --vsan_id_b=200 \
    --zoneset_name_a=zoneset-demo-a \
    --zoneset_name_b=zoneset-demo-b \
    --flag_configure_device_aliases=false \
    --flag_add_zones_to_zonesets=false \
    --flag_activate_zonesets=false
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.
