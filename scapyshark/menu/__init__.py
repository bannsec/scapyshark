
# Base Mix-in class for all menus
class MenuBase(object):
    
    def __init__(self, scapyshark, title, menu_items=None):
        self._scapyshark = scapyshark
        self.title = title

        if menu_items is not None:
            self._menu_items = menu_items
            self._build_menu()

    def open(self):
        """ Open up this menu. """

        max_width = max(len(x.original_widget.get_text()[0]) for x in list(self._menu.original_widget.original_widget.body))
        max_width = max(max_width, len(self._menu.original_widget.title_widget.get_text()[0]))

        overlay = urwid.Overlay(self._menu, self._scapyshark.loop.widget, 'center', max_width+5, 'middle', 20)

        # Register that we have it open
        self._scapyshark._overlays.append({
            'name': 'Main Menu',
            'widget': self._menu,
            'previous_widget': self._scapyshark.loop.widget,
            'enter_handler': self.enter_handler
            })

        # Actually set it
        self._scapyshark.loop.widget = overlay

    def enter_handler(self, focus_widgets):
        """ Handle when enter is clicked on our menu. """
        widget = focus_widgets[-1]
        text = widget.original_widget
        text._enter_handler()

    def _build_menu(self): 

        assert type(self._menu_items) in [list, tuple], 'Unexpected menu_items type of {}'.format(type(self._menu_items))

        # Build the menu
        menu_items = []
        for item, handler in self._menu_items:
            menu_items.append(urwid.AttrMap(urwid.Text(item),'frame','selected'))
            menu_items[-1].original_widget._enter_handler = handler

        menu = urwid.ListBox(urwid.SimpleFocusListWalker(menu_items))
        menu = urwid.LineBox(menu, title=self.title)
        menu = urwid.AttrMap(menu, 'frame')

        self._menu = menu

import urwid

from . import main_menu
