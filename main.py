from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
import ipaddress

class SimpleSDNController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(SimpleSDNController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}  # Stores MAC-to-port mappings
        self.packet_count_per_host = {}  # Dictionary to store packet count per host
        self.packet_count_per_port = {}  # Dictionary to store packet count per port
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handles initial connection with a switch."""
        datapath = ev.msg.datapath
        self._install_table_miss_flow(datapath)
    
    def _install_table_miss_flow(self, datapath):
        """Install a table-miss flow entry to handle unmatched packets."""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Match all packets
        match = parser.OFPMatch()
        # Send unmatched packets to the controller
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        
        # Create a flow mod message
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        flow_mod = parser.OFPFlowMod(
            datapath=datapath, priority=0, match=match, instructions=inst
        )
        # Send the flow mod message to the switch
        datapath.send_msg(flow_mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Handles packets that are sent to the controller."""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # Extract packet data
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        
        # Only handle IPv4 packets
        if eth_pkt.ethertype == ether_types.ETH_TYPE_IP:
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            src_ip = ip_pkt.src
            dst_ip = ip_pkt.dst

            # Check if both source and destination IP are in the same subnet (10.0.0.0/24)
            subnet = ipaddress.IPv4Network('10.0.0.0/24')
            if ipaddress.IPv4Address(src_ip) in subnet and ipaddress.IPv4Address(dst_ip) in subnet:
                self.logger.info(f"Forwarding packet from {src_ip} to {dst_ip}")
                actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            else:
                self.logger.info(f"Dropping packet between {src_ip} and {dst_ip} (different subnets)")
                actions = []  # No actions, effectively drops the packet
        else:
            actions = []

        # Log packet count for host and port
        self.packet_count_per_host[src_ip] = self.packet_count_per_host.get(src_ip, 0) + 1
        self.packet_count_per_port[in_port] = self.packet_count_per_port.get(in_port, 0) + 1

        # Log packet details
        self.logger.info(f"Packet received on port {in_port}. Total packets from {src_ip}: {self.packet_count_per_host[src_ip]}")
        self.logger.info(f"Total packets received on port {in_port}: {self.packet_count_per_port[in_port]}")

        # Send the packet with the appropriate actions or drop it
        if actions:
            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=pkt.data
            )
            datapath.send_msg(out)
