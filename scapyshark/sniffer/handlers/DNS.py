
import logging
logger = logging.getLogger('ScapyShark:Sniffer:Handler:DNS')

import sqlite3
import os
import requests
from zipfile import ZipFile
from io import BytesIO
import scapy
import urwid
from prettytable import PrettyTable
from ...modules import db
from ...window import Window
from ...modules import umbrella

here = os.path.dirname(os.path.realpath(__file__))

create_dns_db = """
CREATE TABLE dns_requests (
    requester text NOT NULL,
    resolver text NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (requester, resolver, name)
    );
"""

def init():
    global init_done
    global discovered_dns_db

    # Init our discovered dns to nothing
    db.execute(create_dns_db)

    init_done = True

def insert_query_record(sniffer, packet):

    try:
        ip = packet[scapy.layers.inet.IP]
    except IndexError:
        ip = packet[scapy.layers.inet6.IPv6]

    udp = packet[scapy.layers.inet.UDP]

    # Handling possible multi-queries
    i = 0
    updated = 0

    while True:

        try:
            dnsqr = packet[scapy.layers.dns.DNSQR][i]
        except IndexError:
            # Guess we're done
            break

        # If this is a response, then the requester/resolver should be reversed
        if udp.sport == 53:
            args = (ip.dst, ip.src, dnsqr.qname.strip(b'.'))
        else:
            args = (ip.src, ip.dst, dnsqr.qname.strip(b'.'))

        updated += db.execute("INSERT OR IGNORE INTO dns_requests (requester, resolver, name) VALUES (?, ?, ?)", args)
        i += 1

    return updated

def _should_i_handle_this(sniffer, packet):
    # Only interested in DNS
    if not packet.haslayer(scapy.layers.dns.DNS):
        return False

    layer = packet[scapy.layers.inet.UDP] if packet.haslayer(scapy.layers.inet.UDP) else packet[scapy.layers.inet.TCP]

    # Only normal DNS... No MDNS
    if layer.sport != 53 and layer.dport != 53:
        return False

    return True


def handle(sniffer, packet):

    updated = 0

    if not _should_i_handle_this(sniffer, packet):
        return

    if packet.haslayer(scapy.layers.dns.DNSQR):
        updated = insert_query_record(sniffer, packet)

    if updated != 0:
        Window.notify_updates("DNS")

###########
# Windows #
###########

class WindowDNSSummary(Window):
    def update(self):

        rows = db.execute('SELECT requester, resolver, group_concat(name, ", ") FROM dns_requests GROUP BY requester, resolver', fetch_all=True)
        table = PrettyTable(['Requester', 'Resolver', 'Names'])
        table.border = False
        table.align['Requester'] = 'l'
        table.align['Resolver'] = 'l'
        table.min_width = 100
        table.max_table_width = self._scapyshark.loop.screen_size[0]-30

        for row in rows:
            table.add_row([row['requester'], row['resolver'], row['group_concat(name, ", ")']])

        # Apparently we have nothing
        if table._rows == []:
            return

        self.text = str(table)

try:
    init_done
except:
    init()

