#!/usr/bin/env python3

import scapy.all
import urwid
from .scrolling import ScrollingListBox
from .sniffer import Sniffer
from .version import version

palette = [
    ('body','black','dark cyan', 'standout'),
    ('header','light gray', 'black'),
    ('key','light cyan', 'black', 'underline'),
    ('title', 'white', 'black',),
    ('frame', 'dark green', 'black'),
    ('selected', 'light green', 'black'),
    ]

class ScapyShark(object):

    def __init__(self):
        self._init_window()
        self.sniffer = Sniffer(self)

        # Keep track of what overlays are open
        self._overlays = []

    def _init_window(self):
        header = 'ScapyShark v{version}'.format(version=version)
        self._header_box = urwid.BoxAdapter(urwid.AttrMap(urwid.Filler(urwid.Text(header, align='center')), 'header'), 1)
        self._footer_box = urwid.BoxAdapter(urwid.AttrMap(urwid.Filler(urwid.Text('No Packets Yet.', align='right')), 'header'), 1)

        # Body
        self._top_box = ScrollingListBox()
        self._middle_box = urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Text('')]))
        self._bottom_box = urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Text('')]))
        
        divider = (1, urwid.Filler(urwid.Divider('\u2500')))
        self._body_pile = urwid.Pile([self._top_box, divider, self._middle_box, divider, self._bottom_box], focus_item=self._top_box)

        # Overarching Frame
        self.frame = urwid.Frame(self._body_pile, header=self._header_box, footer=self._footer_box, focus_part='body')

        # The main loop
        self.loop = urwid.MainLoop(urwid.AttrMap(self.frame, 'frame'), unhandled_input=self.unhandled_input, palette=palette)

    def run(self):
        self.sniffer.start()
        self.loop.run()

    def unhandled_input(self, inp):
        focus_widgets = self.loop.widget.base_widget.get_focus_widgets()

        if inp in ('q','Q'):
            # Q with an overlay up should just pop the overlay
            if self._overlays != []:
                self._pop_overlay()

            # No overlay up, we should quit
            else:
                raise urwid.ExitMainLoop()

        elif inp == 'enter':
            # User hit enter on a packet for more information
            if self._top_box in focus_widgets:
                show_packet_info(self, focus_widgets[-1])

            # Did uer hit enter on an overlay menu
            for overlay in self._overlays:
                if overlay['widget'] in focus_widgets:
                    overlay['enter_handler'](self, focus_widgets)
                    break

        elif inp == 'tab':
            if self._top_box in focus_widgets:
                self._body_pile.set_focus(self._middle_box)
            elif self._middle_box in focus_widgets:
                self._body_pile.set_focus(self._bottom_box)
            elif self._bottom_box in focus_widgets:
                self._body_pile.set_focus(self._top_box)

        elif inp in ('m', 'M'):
            menu.main_menu.open(self)

        elif inp == 'down':
            # Did our menu mess up?
            for overlay in self._overlays:
                if overlay['widget'] in focus_widgets:
                    overlay['widget'].base_widget.focus_position = (overlay['widget'].base_widget.focus_position + 1) % len(overlay['widget'].base_widget.body)
                
        elif inp == 'up':
            # Did our menu mess up?
            for overlay in self._overlays:
                if overlay['widget'] in focus_widgets:
                    overlay['widget'].base_widget.focus_position = (overlay['widget'].base_widget.focus_position - 1) % len(overlay['widget'].base_widget.body)

    def _pop_overlay(self):
        """ Remove top overlay. """
        overlay = self._overlays.pop()
        self.loop.widget = overlay['previous_widget']
        
def main():
    shark = ScapyShark()
    shark.run()


if __name__ == '__main__':
    main()

from .packetinfo import show_packet_info
from . import menu
