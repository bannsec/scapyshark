
import logging
logger = logging.getLogger(__name__)

from . import db
from ..window import Window

# O'Riely 80211 Wireless Networks Chapter 4

create_dot11_ap_db = """
CREATE TABLE dot11_ap (
    ssid text,
    bssid text,
    channel smallint,
    oui int,
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

def record_ssid(ssid, bssid, frequency):
    assert isinstance(ssid, bytes), "SSID needs to be type bytes, not {}".format(type(ssid))
    assert isinstance(bssid, bytes), "BSSID needs to be type bytes, not {}".format(type(bssid))
    assert isinstance(frequency, int), "Frequency needs to be integer, not {}".format(type(frequency))

    if frequency in dot11_types.dot11_type_channels:
        channel = dot11_types.dot11_type_channels[frequency]

    else:
        channel = min(dot11_types.dot11_type_channels, key=lambda x:abs(x-frequency))
    
    updated = db.execute('INSERT OR IGNORE INTO dot11_ap (ssid, bssid, oui, channel) VALUES (?, ?, ?, ?)',
            (ssid,
            bssid,
            int(bssid.replace(b":",b"")[:6],16),
            channel
            ))

    if updated != 0:
        Window.notify_updates("Dot11")

###########
# Windows #
###########

class WindowAPSummary(Window):
    def update(self):
        rows = db.execute("SELECT ssid, bssid, group_concat(channel, ', ') AS channels, name AS oui_vendor FROM dot11_ap LEFT JOIN oui_lookup ON dot11_ap.oui = oui_lookup.prefix GROUP BY ssid, bssid ORDER BY ssid", fetch_all=True)

        if rows == []:
            return
        
        table = PrettyTable(['SSID', 'BSSID', 'Channel'])
        table.border = False
        table.align['SSID'] = 'l'
        table.align['BSSID'] = 'l'
        table.align['Channel'] = 'l'
        
        for row in rows:
            ssid = row['ssid'].decode('utf-8', errors='replace')
            if ssid == '':
                ssid = "<hidden>"

            bssid = row['bssid'].decode('utf-8', errors='replace')

            if row['oui_vendor'] is not None:
                bssid += " ({})".format(row['oui_vendor'])

            channel = row['channels']

            table.add_row([ssid, bssid, channel])

        self._update_box_text(str(table))

from . import dot11_types
