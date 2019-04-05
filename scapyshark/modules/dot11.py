
import logging
logger = logging.getLogger(__name__)

from . import db
from ..helpers import update_popup_box_text, update_windows

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

@update_windows
def record_ssid(ssid, bssid):
    assert isinstance(ssid, bytes), "SSID needs to be type bytes, not {}".format(type(ssid))
    assert isinstance(bssid, bytes), "BSSID needs to be type bytes, not {}".format(type(bssid))
    
    db.execute('INSERT OR IGNORE INTO dot11_ap (ssid, bssid) VALUES (?, ?)', (ssid, bssid))

###########
# Windows #
###########

def _window_show_ap_summary(scapyshark):
    global windows_updates

    _window_update_ap_summary(scapyshark)
    scapyshark._dialogue_general(window_ap_summary, title='802.11 AP Summary', close_handler=_window_close_ap_summary)
    windows_updates.append(_window_update_ap_summary)

def _window_close_ap_summary(scapyshark):
    global windows_updates
    windows_updates.remove(_window_update_ap_summary)

def _window_update_ap_summary(scapyshark):
    rows = db.execute("SELECT * FROM dot11_ap", fetch_all=True)

    if rows == []:
        return
    
    table = PrettyTable(['SSID', 'BSSID'])
    table.border = False
    table.align['SSID'] = 'l'
    table.align['BSSID'] = 'l'
    
    for row in rows:
        table.add_row([row['ssid'].decode('utf-8', errors='replace'), row['bssid'].decode('utf-8', errors='replace')])

    update_popup_box_text(window_ap_summary, str(table))


