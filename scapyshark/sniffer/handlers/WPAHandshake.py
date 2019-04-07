
import collections
import scapy.all
import struct
import os

#
# Using EAPOL Key_Information flags as indicator for which handshake step we're on
#

steps = {
 1: 0x8a,
 2: 0x10a,
 3: 0x13ca,
 4: 0x30a
 }

steps_rev = {y:x for x,y in steps.items()}


def handle(sniffer, packet):

    if scapy.layers.eap.EAPOL not in packet:
        return

    # As of writing, EAPOL in scapy doesn't have the fields parsed, thus I'm loading the raw data after it, and specifically pulling out this field
    key_information_field = struct.unpack(">h", packet[scapy.layers.eap.EAPOL][1].load[1:3])[0]

    # Which step are we on
    step = steps_rev[key_information_field]

    if step in [1,3]:
        client = packet[scapy.layers.dot11.Dot11].addr1
        access_point = packet[scapy.layers.dot11.Dot11].addr2

    else:
        client = packet[scapy.layers.dot11.Dot11].addr2
        access_point = packet[scapy.layers.dot11.Dot11].addr1

    index = access_point + client

    # Only need one handshake. Bail out.
    if WPAHandshake.has_handshake(access_point):
        return

    # Throw away previous failed attempts
    del handshakes[index][step-1:]

    handshakes[index].append(packet)

    # Trying to not assume the step number is always right. I.e.: make sure we actually have all the packets.
    if len(handshakes[index]) == 4:
        WPAHandshake.save_handshake(handshakes[index], access_point)
        WPAHandshake.write_handshake_pcap(
                os.path.join(sniffer._shark._args.output, "wpa_handshake_" + sanitize_filename(access_point) + ".pcap"),
                access_point)

def init():
    global handshakes
    
    # Key == client:access_point
    # Value[i] == handshake step i
    handshakes = collections.defaultdict(list)

try:
    handshakes
except:
    init()

from ...modules import WPAHandshake
from ...helpers import sanitize_filename
