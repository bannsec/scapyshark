
from . import MenuBase

def build_menu(scapyshark):
    global menu
    global window_ap_summary
    global window_probe_summary

    window_ap_summary = dot11.WindowAPSummary(scapyshark, title='802.11 AP Summary', update_on='Dot11')
    window_probe_summary = dot11.WindowProbeSummary(scapyshark, title='802.11 Probe Summary', update_on='Dot11Probe')

    menu_items = [
        ('Access Points', window_ap_summary.show),
        ('Probe Requests', window_probe_summary.show),
        ('Close', scapyshark._pop_overlay)
    ]

    menu = MenuBase(scapyshark, title='802.11', menu_items=menu_items)
    return menu

from ..modules import dot11
