# gNMI Collector

A Python-based gNMI (gRPC Network Management Interface) collector for network telemetry. This single-process external service subscribes to interface, LLDP, and ARP events from cEOS and SONiC devices, outputting structured JSON lines to stdout.

## Features

- **Single-process design**: Lightweight and easy to deploy
- **Multi-vendor support**: Works with both Arista cEOS and SONiC devices
- **OpenConfig paths**: Uses standard OpenConfig models for portability
- **Telemetry streaming**: Subscribes to real-time interface, LLDP, and ARP updates
- **JSON output**: Structured JSON lines to stdout for easy integration with downstream systems
- **Insecure mode**: Configured for lab environments (no TLS/SSL)
- **YAML configuration**: Easy-to-edit device and path configurations

## Important Note

⚠️ **Single Device Limitation**: This basic implementation processes devices sequentially. Since gNMI subscriptions are blocking (they continuously stream data), only the **first device** in `config/devices.yaml` will be actively monitored.

**For monitoring multiple devices**, use one of these approaches:
- Run multiple collector instances (one per device)
- Modify the collector to use threading or asyncio for concurrent subscriptions
- Use a process manager like systemd to run multiple instances

## Requirements

- Python 3.7 or higher
- Access to cEOS or SONiC devices with gNMI enabled

## Installation

1. **Navigate to the collector directory**:
   ```bash
   cd gnmi-collector
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Configuration

### Device Configuration

Edit `config/devices.yaml` to configure your network devices:

```yaml
devices:
  - name: ceos-spine1
    type: ceos          # Device type: 'ceos' or 'sonic'
    host: 192.168.1.10  # Device IP address
    port: 6030          # gNMI port (default: 6030 for cEOS, 8080 for SONiC)
    username: admin     # gNMI username
    password: admin     # gNMI password
```

**Device Types**:
- `ceos`: Arista cEOS devices
- `sonic`: SONiC network operating system devices

### Path Configuration

The collector uses separate path configurations for each device type:

- **`paths/ceos.yaml`**: OpenConfig paths for cEOS devices
- **`paths/sonic.yaml`**: OpenConfig paths for SONiC devices

These files define which telemetry paths to subscribe to. The default configurations include:
- Interface statistics and operational status
- LLDP neighbor information
- ARP table entries

You can customize these paths based on your monitoring requirements.

## Usage

### Basic Usage

Run the collector with default settings:

```bash
python collector.py
```

The collector will:
1. Load device configurations from `config/devices.yaml`
2. Connect to each device via gNMI (insecure mode)
3. Subscribe to the configured telemetry paths
4. Output JSON-formatted telemetry updates to stdout
5. Log operational messages to stderr

### Custom Configuration Directories

Specify custom configuration directories:

```bash
python collector.py --config-dir /path/to/config --paths-dir /path/to/paths
```

### Output Redirection

Redirect JSON output to a file:

```bash
python collector.py > telemetry.jsonl 2> collector.log
```

Or pipe to another tool:

```bash
python collector.py | jq .
```

### Running as a Service

For production deployments, consider running the collector as a systemd service or in a container.

## Output Format

Each telemetry update is output as a single-line JSON object:

```json
{
  "device": "ceos-spine1",
  "device_type": "ceos",
  "host": "192.168.1.10",
  "timestamp": 1706918400.123456,
  "data": {
    "update": {
      "path": "/interfaces/interface[name=Ethernet1]/state/counters",
      "val": { ... }
    }
  }
}
```

**Fields**:
- `device`: Device name from configuration
- `device_type`: Type of device (ceos or sonic)
- `host`: Device IP address
- `timestamp`: Unix timestamp when the update was received
- `data`: Raw gNMI telemetry data from the device

## Device Setup

### Enabling gNMI on cEOS

```
ceos-spine1(config)# management api gnmi
ceos-spine1(config-mgmt-api-gnmi)# transport grpc default
ceos-spine1(config-mgmt-api-gnmi)# provider eos-native
```

Default port: 6030

### Enabling gNMI on SONiC

SONiC typically has gNMI enabled by default on port 8080. Verify with:

```bash
sudo systemctl status gnmi
```

## Troubleshooting

### Connection Issues

- Verify device IP addresses and ports in `config/devices.yaml`
- Ensure gNMI is enabled on the target devices
- Check network connectivity: `ping <device-ip>`
- Verify credentials are correct

### No Telemetry Data

- Check that the paths in `paths/*.yaml` are supported by your devices
- Use the device's CLI to verify the paths exist
- Check device logs for gNMI errors

### Python Dependencies

If you encounter issues installing `pygnmi`:

```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## Architecture

The collector follows a simple architecture:

1. **Configuration Loading**: Reads YAML configurations for devices and paths
2. **gNMI Connection**: Establishes insecure gRPC connections to devices
3. **Subscription**: Creates ON_CHANGE subscriptions for configured paths
4. **Stream Processing**: Receives and processes telemetry updates
5. **JSON Output**: Formats and outputs data to stdout

## Security Note

⚠️ **This collector is configured for lab environments** and uses insecure gNMI connections (no TLS). For production deployments, enable TLS by:
- Modifying the `gNMIclient` instantiation in `collector.py`
- Setting `insecure=False`
- Providing appropriate certificates

## Integration Examples

### With Kafka

```bash
python collector.py | kafkacat -P -b localhost:9092 -t network-telemetry
```

### With InfluxDB

```bash
python collector.py | your-influxdb-writer
```

### With Logstash

Configure Logstash to read from stdin and process the JSON lines.

## Contributing

When adding support for new device types:
1. Create a new paths file: `paths/<device-type>.yaml`
2. Add device entries to `config/devices.yaml` with the appropriate type
3. Test the configuration with your devices

## License

This project is part of the sdn-architecture repository.
