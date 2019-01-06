

def build_menu(scapyshark):
    global main_menu
    stats_submenu = stats.build_menu(scapyshark)
    research_submenu = research.build_menu(scapyshark)

    menu_items = [
        ('Stats', stats_submenu.open),
        ('Research', research_submenu.open),
        ('Close', scapyshark._pop_overlay)
    ]

    main_menu = MenuBase(scapyshark, title='Main Menu', menu_items=menu_items)
    return main_menu

from . import MenuBase
from . import stats
from . import research
