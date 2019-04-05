
import logging
logger = logging.getLogger(__name__)

import scapy.all
from ...helpers import iter_layers_by_type

from ...modules.dot11_types import *
from ...modules import dot11

def handle(sniffer, packet):
    
    if scapy.layers.dot11.Dot11Beacon in packet:
        _handle_dot11beacon(sniffer, packet)

    else:
        # We didn't handle it
        return

    # Generic call to update things or not
    #for updater in windows_updates:
    #    updater(sniffer._shark)

def _handle_dot11beacon(sniffer, packet):

    ssid = None
    bssid = packet[scapy.layers.dot11.Dot11FCS].addr2.encode('latin-1')
    
    for layer in iter_layers_by_type(packet, scapy.layers.dot11.Dot11Elt, allow_subclass=True):

        # If we're looking at the SSID field of the beacon
        if layer.ID == dot11_type_elt_s2i['SSID']:
            ssid = layer.info

    if ssid is None:
        logger.warn("Parsed Dot11 Beacon but couldn't find SSID...")
        return

    # No ssid specified (hidden)
    if ssid == b'\x00':
        ssid = b''

    dot11.record_ssid(ssid=ssid, bssid=bssid)
