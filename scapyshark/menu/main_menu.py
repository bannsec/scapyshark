
from . import MenuBase

def build_menu(scapyshark):
    global main_menu

    menu_items = [
        ('Conversations - DOT', scapyshark._top_box.packets.conversations),
        ('Close', scapyshark._pop_overlay)
    ]

    main_menu = MenuBase(scapyshark, title='Main Menu', menu_items=menu_items)
    return main_menu
