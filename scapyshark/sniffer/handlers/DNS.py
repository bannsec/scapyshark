
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
    global conn
    global discovered_dns_db
    global window_dns_summary
    global windows_updates

    windows_updates = []

    # Init our discovered dns to nothing
    db.execute(create_dns_db)

    logger.info('Performing init.')

    conn = sqlite3.connect(os.path.join(here, 'dns.db'))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute('SELECT count(*) FROM umbrella')

        # Check that we have a full table and not partial
        r = next(c)
        if r['count(*)'] != 1000000:
            build_umbrella_table()

    except:
        # Table doesn't exist
        build_umbrella_table()

    window_dns_summary = urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Text('Nothing yet...')]))
    c.close()

def insert_query_record(sniffer, packet):

    try:
        ip = packet[scapy.layers.inet.IP]
    except IndexError:
        ip = packet[scapy.layers.inet6.IPv6]

    udp = packet[scapy.layers.inet.UDP]

    # Handling possible multi-queries
    i = 0
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

        db.execute("INSERT OR IGNORE INTO dns_requests (requester, resolver, name) VALUES (?, ?, ?)", args)
        i += 1

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

    if not _should_i_handle_this(sniffer, packet):
        return

    if packet.haslayer(scapy.layers.dns.DNSQR):
        insert_query_record(sniffer, packet)

    # Generic call to update things or not
    for updater in windows_updates:
        updater(sniffer._shark)

############
# Umbrella #
############

def build_umbrella_table():

    print('Building DNS database. Please be patient... ', flush=True, end='')

    # Blow away table if it is there
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS umbrella''')

    c.execute('''CREATE TABLE umbrella (rank int, dns text PRIMARY KEY)''')
    r = requests.get('http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip')
    zip_f = BytesIO(r.content)
    z = ZipFile(zip_f,'r')
    csv = z.read(z.filelist[0]).decode().strip() # Extract csv

    for line in csv.split('\n'):
        line = line.strip()
        c.execute('''INSERT INTO umbrella values (?, ?)''', line.split(','))

    conn.commit()
    c = conn.cursor()
    c.execute('''VACUUM''')
    conn.commit()
    c.close()

    print('OK')

def check_umbrella(dns):
    """ Return umbrella rank for the given domain name. """
    c = conn.cursor()
    c.execute('''SELECT * FROM umbrella WHERE dns == ?''', (dns,))

    try:
        r = next(c)
        c.close()
    except:
        c.close()
        # This domain name wasn't found
        return None

    return r['rank']

###########
# Windows #
###########

def _window_show_dns_summary(scapyshark):
    global windows_updates

    _window_update_dns_summary(scapyshark)
    scapyshark._dialogue_general(window_dns_summary, title='DNS Summary', close_handler=_window_close_dns_summary)
    windows_updates.append(_window_update_dns_summary)

def _window_close_dns_summary(scapyshark):
    global windows_updates
    windows_updates.remove(_window_update_dns_summary)

def _window_update_dns_summary(scapyshark):
    """Update the dns summary window with the current information."""

    rows = db.execute('SELECT requester, resolver, group_concat(name, ", ") FROM dns_requests GROUP BY requester, resolver', fetch_all=True)
    table = PrettyTable(['Requester', 'Resolver', 'Names'])
    table.border = False
    table.align['Requester'] = 'l'
    table.align['Resolver'] = 'l'
    table.min_width = 100
    table.max_table_width = scapyshark.loop.screen_size[0]-30

    for row in rows:
        table.add_row([row['requester'], row['resolver'], row['group_concat(name, ", ")']])

    # Apparently we have nothing
    if table._rows == []:
        window_dns_summary.body = [urwid.Text('Nothing yet...')]

    i = 0
    current_len = len(list(window_dns_summary.body))

    for line in str(table).split('\n'):
        
        new_line = urwid.Text(line)

        # Attempting to utilizing the 'smarts' in urwid to only update lines that need to be updated

        # Our new table has more rows than the original
        if i >= current_len:
            window_dns_summary.body.append(new_line)

        # Changed line
        elif new_line != window_dns_summary.body[i]:
            window_dns_summary.body[i] = new_line

        # Line must be the same as old line
        i += 1

    # Remove any excess lines
    del window_dns_summary.body[i:]

try:
    conn
except:
    init()

