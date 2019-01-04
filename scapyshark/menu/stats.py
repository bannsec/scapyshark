
from . import MenuBase

def build_menu(scapyshark):
    global menu

    menu_items = [
        ('Conversations - DOT', scapyshark._top_box.packets.conversations),
        ('Close', scapyshark._pop_overlay)
    ]

    menu = MenuBase(scapyshark, title='Stats', menu_items=menu_items)
    return menu
