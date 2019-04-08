
import logging
logger = logging.getLogger(__name__)

import scapy.all
from ...helpers import iter_layers_by_type

from ...modules.dot11_types import *
from ...modules import dot11

def handle(sniffer, packet):
    
    if scapy.layers.dot11.Dot11Beacon in packet:
        _handle_dot11beacon(sniffer, packet)

    elif scapy.layers.dot11.Dot11ProbeReq in packet:
        _handle_dot11probereq(sniffer, packet)

    else:
        # We didn't handle it
        return

def _handle_dot11probereq(sniffer, packet):
    
    ssid = None

    if scapy.layers.dot11.Dot11FCS in packet:
        mac = packet[scapy.layers.dot11.Dot11FCS].addr2.encode('latin-1')
    else:
        mac = packet.addr2.encode('latin-1')

    for layer in iter_layers_by_type(packet, scapy.layers.dot11.Dot11Elt, allow_subclass=True):

        # If we're looking at the SSID field of the beacon
        if layer.ID == dot11_type_elt_s2i['SSID']:
            ssid = layer.info
            break

    # This is a general probe request.
    if ssid == b'':
        return

    dot11.record_probe(ssid, mac)


def _handle_dot11beacon(sniffer, packet):

    ssid = None

    if scapy.layers.dot11.Dot11FCS in packet:
        bssid = packet[scapy.layers.dot11.Dot11FCS].addr2.encode('latin-1')
    else:
        bssid = packet.addr2.encode('latin-1')

    # TODO: Handle Multiple cipher options?
    # TODO: Handle different cipher from pairwise vs groupwise
    if scapy.layers.dot11.Dot11EltRSN in packet:
        cipher_i2s = packet[scapy.layers.dot11.Dot11EltRSN].pairwise_cipher_suites[0].fieldtype['cipher'].i2s
        pairwise_cipher = packet[scapy.layers.dot11.Dot11EltRSN].pairwise_cipher_suites[0].cipher
        pairwise_cipher = cipher_i2s[pairwise_cipher]
        
        group_cipher = packet[scapy.layers.dot11.Dot11EltRSN].group_cipher_suite.cipher
        group_cipher = cipher_i2s[group_cipher]
    
    else:
        # Open WiFi
        pairwise_cipher = None
        group_cipher = None

    for layer in iter_layers_by_type(packet, scapy.layers.dot11.Dot11Elt, allow_subclass=True):

        # If we're looking at the SSID field of the beacon
        if layer.ID == dot11_type_elt_s2i['SSID']:
            ssid = layer.info

        elif layer.ID == dot11_type_elt_s2i['DS Parameter Set']:
            channel = layer.info[0]

    if ssid is None:
        logger.warn("Parsed Dot11 Beacon but couldn't find SSID...")
        return

    # No ssid specified (hidden)
    if ssid == b'\x00':
        ssid = b''

    # Check for WEP
    if pairwise_cipher is None and packet[scapy.layers.dot11.Dot11Beacon].cap.privacy:
        pairwise_cipher = "WEP"
        group_cipher = "WEP"

    dot11.record_ssid(ssid=ssid, bssid=bssid, channel=channel, pairwise_cipher=pairwise_cipher, group_cipher=group_cipher)
