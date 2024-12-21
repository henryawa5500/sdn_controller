# sdn_controller
A basic Software-defined network controller

# Simple SDN Controller with Ryu Framework

## Overview
This project provides a simple Software-Defined Networking (SDN) controller built using the Ryu framework. It demonstrates basic SDN functionality, such as processing packets, setting up flow entries, and interacting with OpenFlow switches.

## Features
- Handles basic packet-in events
- Sets up table-miss flow entries for unmatched packets
- Floods packets to all ports as a default forwarding behaviour
- Demonstrates key concepts of SDN using Ryu



## Prerequisites
1. **Python**: Ensure Python 3.9 or later is installed on your system.
2. **Mininet**: Install Mininet for simulating the SDN environment.
3. **Ryu Framework**: The project uses Ryu as the SDN controller framework.
4. **Virtual Environment**: Create and activate a Python virtual environment for dependency management.



## Installation and Setup

### Clone the Repository
```bash
git clone git@github.com:imosudi/sdn_controller.git
cd sdn_controller/
```

### Set Up Virtual Environment
```bash
python3.9 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```



## Running the Controller
1. Start the Ryu controller:
   ```bash
   ryu-manager main.py
   ```
   The controller will listen for OpenFlow-enabled switches and process events such as `PacketIn`.

2. Launch a Mininet environment (in another terminal window):
   ```bash
   sudo mn --controller=remote,ip=127.0.0.1,port=6633 --topo=single,3
   ```
   Replace `single,3` with your preferred Mininet topology.

3. Test connectivity in Mininet:
   ```bash
   pingall
   ```



## Code Explanation

### Key Components in `main.py`
1. **Switch Features Handler**: Sets up table-miss flow entries for unmatched packets.
2. **Packet-In Handler**: Processes packets sent to the controller by OpenFlow switches and floods them as the default action.

### Example Flow Mod Installation
```python
def _install_table_miss_flow(self, datapath):
    match = datapath.ofproto_parser.OFPMatch()
    actions = [datapath.ofproto_parser.OFPActionOutput(datapath.ofproto.OFPP_CONTROLLER)]
    inst = [datapath.ofproto_parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS, actions)]
    flow_mod = datapath.ofproto_parser.OFPFlowMod(
        datapath=datapath, priority=0, match=match, instructions=inst
    )
    datapath.send_msg(flow_mod)
```



## Troubleshooting
- **Ryu Import Errors**: Ensure Ryu is installed correctly within your virtual environment using `pip install -r requirements.txt`.
- **Mininet Connection Issues**: Verify that Mininet is configured to use the remote controller and matches the IP and port of your Ryu controller.
- **Ping Failures**: Ensure proper configuration of flow entries in `main.py` or debug using Ryu logs.



## Contributions
Contributions are welcome! Feel free to fork the repository and create pull requests.



## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
