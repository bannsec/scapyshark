

def init():
    global handshakes
    
    # Dict, key is the bssid of the access point
    handshakes = dict()

def save_handshake(handshake, access_point):
    assert type(handshake) == list and len(handshake) == 4, "Handshake error..."

    if type(access_point) is str:
        access_point = access_point.encode('latin-1', errors='replace')

    handshakes[access_point] = handshake
    updated = db.execute('UPDATE dot11_ap SET found_handshake=1 WHERE dot11_ap.bssid = ?', (access_point,))

    if updated != 0:
        Window.notify_updates("Dot11")


def has_handshake(access_point):
    return access_point in handshakes

def write_handshake_pcap(filename, access_point):

    if type(access_point) is str:
        access_point = access_point.encode('latin-1', errors='replace')

    scapy.utils.wrpcap(filename, handshakes[access_point])


try:
    handshakes
except:
    init()

from . import db
from ..window import Window
import scapy.all
