
import logging
logger = logging.getLogger(__name__)

from . import db
from ..window import Window

# O'Riely 80211 Wireless Networks Chapter 4

create_dot11_ap_db = """
CREATE TABLE dot11_ap (
    ssid text,
    bssid text,
    PRIMARY KEY (ssid, bssid)
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

def record_ssid(ssid, bssid):
    assert isinstance(ssid, bytes), "SSID needs to be type bytes, not {}".format(type(ssid))
    assert isinstance(bssid, bytes), "BSSID needs to be type bytes, not {}".format(type(bssid))
    
    db.execute('INSERT OR IGNORE INTO dot11_ap (ssid, bssid) VALUES (?, ?)', (ssid, bssid))
    Window.notify_updates("Dot11")

###########
# Windows #
###########

class WindowAPSummary(Window):
    def update(self):
        rows = db.execute("SELECT * FROM dot11_ap ORDER BY ssid", fetch_all=True)

        if rows == []:
            return
        
        table = PrettyTable(['SSID', 'BSSID'])
        table.border = False
        table.align['SSID'] = 'l'
        table.align['BSSID'] = 'l'
        
        for row in rows:
            ssid = row['ssid'].decode('utf-8', errors='replace')
            if ssid == '':
                ssid = "<hidden>"

            table.add_row([ssid, row['bssid'].decode('utf-8', errors='replace')])

        self._update_box_text(str(table))

