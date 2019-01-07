
from . import MenuBase

def build_menu(scapyshark):
    global menu

    menu_items = [
        ('DNS', lambda : 1),
        ('Test Menu', lambda: scapyshark._dialogue_ok('blerg', title='this is my title')),
        ('Close', scapyshark._pop_overlay)
    ]

    menu = MenuBase(scapyshark, title='Research', menu_items=menu_items)
    return menu
