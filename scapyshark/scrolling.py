from urwid import SimpleFocusListWalker, ListBox, Text, AttrMap
import datetime
import scapy

class ScrollingListBox(ListBox):

    def __init__(self):
        self.walker = SimpleFocusListWalker([])
        self.packets = scapy.plist.PacketList()
        super(ScrollingListBox, self).__init__(self.walker)

    def add(self, message, packet):
        """

        Args:
            message (str): Text message that will appear
            packet (Scapy packet): Packet that corresponds to this entry.
        """
        txt = AttrMap(Text(message), 'frame', 'selected')
        self.walker.append(txt)
        self.packets.append(packet)

        currently_selected = self.get_focus()
        if isinstance(currently_selected, (list, tuple)):
            currently_selected = currently_selected[0]
        
        # This ensures auto scrolling only engages if our selected item is the bottom one
        if len(self.walker) <= 1 or currently_selected is self.walker[-2]:
            self.set_focus(len(self.walker)-1)

    def get_packet(self, message):
        """ Given message, return the corresponding packet. """
        return self.packets[self.walker.index(message)]

    def _keypress_up(self, size):
        # TODO: Not sure why key up is failing like this... Really need to figure out root cause
        #out = super(ScrollingListBox, self)._keypress_up(size)
        
        try:
            self.set_focus(self.walker.prev_position(self.walker.focus))
            return None # No more handling needed
        except IndexError:
            # IndexError is expected when we're at the top of the list
            return True

    def _keypress_down(self, size):
        # TODO: Not sure why key up is failing like this... Really need to figure out root cause (jumping down a page before incrementing down)
        
        try:
            self.set_focus(self.walker.next_position(self.walker.focus))
            return None # No more handling needed
        except IndexError:
            # IndexError is expected when we're at the top of the list
            return True

