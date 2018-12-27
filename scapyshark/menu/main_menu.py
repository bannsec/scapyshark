
ITEM_CLOSE = 'Close'

menu_items = [
    ITEM_CLOSE,
]

def open(scapyshark):
    """ Open up this menu. """
    global menu

    overlay = urwid.Overlay(menu, scapyshark.loop.widget, 'center', 20, 'middle', 20)

    # Register that we have it open
    scapyshark._overlays.append({
        'name': 'Main Menu',
        'widget': menu,
        'previous_widget': scapyshark.loop.widget,
        'enter_handler': enter_handler
        })

    # Actually set it
    scapyshark.loop.widget = overlay

def enter_handler(scapyshark, focus_widgets):
    """ Handle when enter is clicked on our menu. """
    widget = focus_widgets[-1]

    text = widget.original_widget.get_text()[0]

    if text == ITEM_CLOSE:
        scapyshark._pop_overlay()


import urwid

try:
    menu
except:
    
    # Build the menu
    menu_items = [urwid.AttrMap(urwid.Text(item),'frame','selected') for item in menu_items]
    menu = urwid.ListBox(urwid.SimpleFocusListWalker(menu_items))
    menu = urwid.LineBox(menu, title='Main Menu')
    menu = urwid.AttrMap(menu, 'frame')
