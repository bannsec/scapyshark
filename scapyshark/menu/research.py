
from . import MenuBase

def build_menu(scapyshark):
    global menu

    dot11_submenu = dot11.build_menu(scapyshark)

    edit = {
        'caption': 'What you say: ',
        'edit_text': 'This is the edit text',
        'multiline': True,
        'align': 'left',
        'allow_tab': False,
    }

    buttons = []
    buttons.append(urwid.Button('Yes'))
    buttons.append(urwid.Button('No'))
    buttons.append(urwid.Button('Cancel', on_press= lambda _: scapyshark._pop_overlay()))

    def blerg(x):
        pass

    menu_items = [
        ('DNS', lambda: DNS._window_show_dns_summary(scapyshark)),
        ('802.11', dot11_submenu.open),
        ('Test Menu', lambda: scapyshark._dialogue_general('blerg', title='this is my title', edit=edit, buttons=buttons, edit_enter_handler=blerg)),
        ('Close', scapyshark._pop_overlay)
    ]

    menu = MenuBase(scapyshark, title='Research', menu_items=menu_items)
    return menu

import urwid
from ..sniffer.handlers import DNS
from . import dot11
