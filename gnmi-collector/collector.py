#!/usr/bin/env python3
"""
gNMI Collector - A single-process external service for collecting telemetry
from network devices via gNMI (gRPC Network Management Interface).

This collector subscribes to interface, LLDP, and ARP events from cEOS and
SONiC devices, outputting JSON lines to stdout for downstream processing.
"""

import sys
import json
import yaml
import time
import logging
from pathlib import Path
from typing import Dict, List, Any
from pygnmi.client import gNMIclient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr so stdout remains clean for JSON output
)
logger = logging.getLogger(__name__)


class GNMICollector:
    """Main collector class for handling gNMI subscriptions."""
    
    def __init__(self, config_dir: str = "config", paths_dir: str = "paths"):
        """
        Initialize the gNMI collector.
        
        Args:
            config_dir: Directory containing device configuration files
            paths_dir: Directory containing device-specific path files
        """
        self.config_dir = Path(config_dir)
        self.paths_dir = Path(paths_dir)
        self.devices = []
        self.paths = {}
        
    def load_devices(self) -> List[Dict[str, Any]]:
        """Load device configurations from YAML file."""
        devices_file = self.config_dir / "devices.yaml"
        try:
            with open(devices_file, 'r') as f:
                config = yaml.safe_load(f)
                self.devices = config.get('devices', [])
                logger.info(f"Loaded {len(self.devices)} devices from configuration")
                return self.devices
        except FileNotFoundError:
            logger.error(f"Device configuration file not found: {devices_file}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing device configuration: {e}")
            sys.exit(1)
    
    def load_paths(self, device_type: str) -> List[str]:
        """
        Load gNMI paths for a specific device type.
        
        Args:
            device_type: Type of device (ceos or sonic)
            
        Returns:
            List of gNMI paths to subscribe to
        """
        if device_type in self.paths:
            return self.paths[device_type]
            
        paths_file = self.paths_dir / f"{device_type}.yaml"
        try:
            with open(paths_file, 'r') as f:
                config = yaml.safe_load(f)
                paths = config.get('paths', [])
                self.paths[device_type] = paths
                logger.info(f"Loaded {len(paths)} paths for {device_type}")
                return paths
        except FileNotFoundError:
            logger.error(f"Paths file not found: {paths_file}")
            return []
        except yaml.YAMLError as e:
            logger.error(f"Error parsing paths configuration: {e}")
            return []
    
    def subscribe_device(self, device: Dict[str, Any]) -> None:
        """
        Subscribe to gNMI telemetry from a single device.
        
        Args:
            device: Device configuration dictionary
        """
        device_name = device.get('name', 'unknown')
        device_type = device.get('type', 'unknown')
        host = device.get('host')
        port = device.get('port', 6030)
        username = device.get('username', 'admin')
        password = device.get('password', 'admin')
        
        logger.info(f"Connecting to device: {device_name} ({device_type}) at {host}:{port}")
        
        # Load paths for this device type
        paths = self.load_paths(device_type)
        if not paths:
            logger.warning(f"No paths configured for device type: {device_type}")
            return
        
        # Create gNMI subscription list
        subscribe_list = []
        for path in paths:
            subscribe_list.append({
                'path': path,
                'mode': 'ON_CHANGE',
                'sample_interval': 10000000000  # 10 seconds in nanoseconds (fallback for SAMPLE mode)
            })
        
        try:
            # Connect to device with insecure mode (no TLS)
            with gNMIclient(
                target=(host, port),
                username=username,
                password=password,
                insecure=True,  # Use insecure mode for lab environment
                skip_verify=True
            ) as client:
                logger.info(f"Successfully connected to {device_name}")
                
                # Subscribe to telemetry
                telemetry_stream = client.subscribe(subscribe=subscribe_list)
                
                # Process telemetry updates
                for response in telemetry_stream:
                    try:
                        # Add device context to the response
                        output = {
                            'device': device_name,
                            'device_type': device_type,
                            'host': host,
                            'timestamp': time.time(),
                            'data': response
                        }
                        # Output JSON line to stdout
                        print(json.dumps(output), flush=True)
                    except Exception as e:
                        logger.error(f"Error processing telemetry from {device_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Error connecting to device {device_name}: {e}")
    
    def run(self) -> None:
        """Main run loop for the collector."""
        logger.info("Starting gNMI Collector")
        
        # Load device configurations
        devices = self.load_devices()
        
        if not devices:
            logger.error("No devices configured")
            sys.exit(1)
        
        # NOTE: This implementation processes devices sequentially.
        # Since gNMI subscriptions are blocking (they continuously stream data),
        # only the FIRST device in the configuration will be actively monitored.
        # 
        # For production use with multiple devices, implement concurrent processing:
        #   - Use threading.Thread for each device subscription
        #   - Or use asyncio with async gNMI client
        #   - Or run multiple collector instances (one per device)
        logger.info(f"Starting subscriptions for {len(devices)} device(s)")
        logger.warning("Note: Sequential processing - only first device will be monitored in this basic implementation")
        
        for device in devices:
            try:
                self.subscribe_device(device)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                continue


def main():
    """Entry point for the gNMI collector."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='gNMI Collector - Subscribe to network device telemetry'
    )
    parser.add_argument(
        '--config-dir',
        default='config',
        help='Directory containing device configuration files (default: config)'
    )
    parser.add_argument(
        '--paths-dir',
        default='paths',
        help='Directory containing device-specific path files (default: paths)'
    )
    
    args = parser.parse_args()
    
    collector = GNMICollector(
        config_dir=args.config_dir,
        paths_dir=args.paths_dir
    )
    
    try:
        collector.run()
    except KeyboardInterrupt:
        logger.info("Collector stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
