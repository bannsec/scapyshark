from urwid import SimpleFocusListWalker, ListBox, Text
import datetime

class ScrollingListBox(ListBox):

    def __init__(self):
        self.walker = SimpleFocusListWalker([])
        super(ScrollingListBox, self).__init__(self.walker)

    def add(self, message):
        txt = Text(message)
        self.walker.append(txt)
        self.set_focus(len(self.walker)-1)
