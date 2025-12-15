4.1 The Configuration Orchestrator (Backend)
The Orchestrator is the "Brain" of the operation. It isolates business logic from network protocols.

Responsibility: It translates abstract "Intent" (Business Goal) into concrete "Configuration" (Device Payload).

Internal Pipeline:

Template Engine (Jinja2): Loads vendor-specific templates (e.g., sonic_vlan.j2 vs cisco_vlan.j2) based on the device metadata from the Inventory Service.

Variable Injector: Merges user input (VLAN ID: 100) with global policies (DNS, NTP servers) and inventory data (Loopback IP).

Validator: Runs a dry-run check against the specific YANG schema constraints before contacting ODL.

Transaction Manager: Wraps the ODL interaction in a transaction. If ODL fails, the database rolls back to the previous state.

4.2 The OpenDaylight Southbound Interface (SBI)
ODL acts as the "Driver Layer." Its job is to maintain the connection and normalize the transport.

The "Mount Point" Strategy:

Every device (SONiC or OEM) is represented as a Node in the ODL network-topology.

We utilize NETCONF/gNMI Mount Points. This means ODL does not merge all device data into one giant tree; instead, it mounts the device's specific YANG tree under /network-topology/topology/topology-netconf/node/{node-id}/yang-ext:mount/.

Implication: The Backend must query specific mount points to read device config.

Protocol Handling:

For SONiC: We use the gNMI Plugin. The backend pushes OpenConfig JSON. ODL translates this to gNMI Set RPCs.

For OEM (Cisco/Juniper): We use the NETCONF Connector. The backend pushes native/proprietary JSON. ODL translates this to NETCONF Edit-Config RPCs.
