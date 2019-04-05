
from . import MenuBase

def build_menu(scapyshark):
    global menu

    menu_items = [
        ('Access Points', lambda: dot11._window_show_ap_summary(scapyshark)),
        ('Close', scapyshark._pop_overlay)
    ]

    menu = MenuBase(scapyshark, title='802.11', menu_items=menu_items)
    return menu

from ..modules import dot11
