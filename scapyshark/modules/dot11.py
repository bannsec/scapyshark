
import logging
logger = logging.getLogger(__name__)

from . import db
from ..window import Window

# O'Riely 80211 Wireless Networks Chapter 4
# https://dox.ipxe.org/ieee80211_8h_source.html

create_dot11_ap_db = """
CREATE TABLE dot11_ap (
    ssid text,
    bssid text,
    channel smallint,
    oui int,
    pairwise_cipher text,
    group_cipher text,
    found_handshake int,
    PRIMARY KEY (ssid, bssid, channel)
    );
"""

def init():
    global done_init
    global windows_updates
    global window_ap_summary

    windows_updates = []

    db.execute(create_dot11_ap_db)
    done_init = True

    #
    # Setup UI Windows
    #

    window_ap_summary = urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Text('Nothing yet...')]))

import urwid
from prettytable import PrettyTable

try:
    done_init
except:
    init()

def record_ssid(ssid, bssid, channel, pairwise_cipher, group_cipher):
    assert isinstance(ssid, bytes), "SSID needs to be type bytes, not {}".format(type(ssid))
    assert isinstance(bssid, bytes), "BSSID needs to be type bytes, not {}".format(type(bssid))
    assert isinstance(channel, int), "Frequency needs to be integer, not {}".format(type(channel))

    updated = db.execute('INSERT OR IGNORE INTO dot11_ap (ssid, bssid, oui, channel, pairwise_cipher, group_cipher) VALUES (?, ?, ?, ?, ?, ?)',
            (ssid,
            bssid,
            int(bssid.replace(b":",b"")[:6],16),
            channel,
            pairwise_cipher,
            group_cipher
            ))

    if updated != 0:
        Window.notify_updates("Dot11")

###########
# Windows #
###########

class WindowAPSummary(Window):
    def update(self):
        rows = db.execute("SELECT ssid, bssid, group_concat(channel, ', ') AS channels, name AS oui_vendor, pairwise_cipher, group_cipher, found_handshake FROM dot11_ap LEFT JOIN oui_lookup ON dot11_ap.oui = oui_lookup.prefix GROUP BY ssid, bssid ORDER BY ssid", fetch_all=True)

        if rows == []:
            return
        
        table = PrettyTable(['SSID', 'BSSID', 'Channel', 'Auth', 'Handshake'])
        table.border = False
        table.align['SSID'] = 'l'
        table.align['BSSID'] = 'l'
        table.align['Channel'] = 'l'
        table.align['Auth'] = 'l'
        table.align['Handshake'] = 'l'
        
        for row in rows:
            ssid = row['ssid'].decode('utf-8', errors='replace')
            if ssid == '':
                ssid = "<hidden>"

            bssid = row['bssid'].decode('utf-8', errors='replace')

            if row['oui_vendor'] is not None:
                bssid += " ({})".format(row['oui_vendor'])

            channel = row['channels']
            group_cipher = row['group_cipher']
            pairwise_cipher = row['pairwise_cipher']

            if group_cipher is None and pairwise_cipher is None:
                auth = "Open"

            elif group_cipher == pairwise_cipher:
                auth = group_cipher

            else:
                auth = "G: {}, P: {}".format(group_cipher, pairwise_cipher)

            handshake = "Found" if row['found_handshake'] == 1 else ''

            table.add_row([ssid, bssid, channel, auth, handshake])

        self._update_box_text(str(table))

from . import dot11_types
