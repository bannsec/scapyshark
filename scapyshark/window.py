
import collections
import urwid

#
# Base Class for Window displaying stuff
#

class Window(object):

    # Shared list of Window object registrations
    # Key == 'update_on' value, value == window instance pointer
    subscribed_windows = collections.defaultdict(list)

    def __init__(self, scapyshark, title=None, update_on=None):
        """General Window class to display information in ScapyShark

        Args:
            scapyshark (scapyshark.ScapyShark): The running scapyshark class instance.
            title (str, optional): Optional Windows title
            update_on (str, list, optional): Optional string or list of strings
                to watch for updates on. These will be defined by the modules
                so Windows can update only for specific events.
        """

        self._scapyshark = scapyshark
        self.title = title
        self.update_on = update_on

        # Making basic box for now.
        self.box = urwid.ListBox(urwid.SimpleFocusListWalker([urwid.Text('Nothing yet...')]))
        
    def update(self):
        """Update the window with new info. This should be done by the instantiated class."""
        raise NotImplementedError

    def show(self):
        """Pops open the window and registers it for updates."""

        # Initial update
        self.update()

        # Open window
        self._scapyshark._dialogue_general(self.box, title=self.title, close_handler=self._unregister)

        # Register for updates
        self._register()


    def _register(self):
        """Register this object to recieve notifications when something needs updating."""

        for s in self.update_on:
            Window.subscribed_windows[s].append(self)

    def _unregister(self, *args, **kwargs):
        """Remove this window from possible notifications."""

        for s in self.update_on:
            Window.subscribed_windows[s].remove(self)

    def _update_box_text(self, new_string):
        """Convenience method to differentially update the Window's text to hopefully minimize the amount of writing that has to be done to the screen."""

        i = 0
        current_len = len(list(self.box.body))

        for line in new_string.split('\n'):
            
            new_line = urwid.Text(line)

            # Attempting to utilizing the 'smarts' in urwid to only update lines that need to be updated

            # Our new table has more rows than the original
            if i >= current_len:
                self.box.body.append(new_line)

            # Changed line
            elif new_line != self.box.body[i]:
                self.box.body[i] = new_line

            # Line must be the same as old line
            i += 1

        # Remove any excess lines
        del self.box.body[i:]


    ##################
    # Static Methods #
    ##################

    @staticmethod
    def notify_updates(s):
        """Notify any relevant window about update 's'."""
        
        if s in Window.subscribed_windows:
            for window in Window.subscribed_windows[s]:
                window.update()

    
    ##############
    # Properties #
    ##############

    @property
    def title(self):
        """str: What to title this window."""
        return self.__title

    @title.setter
    def title(self, title):
        assert type(title) in [type(None), str], "Unexpected type for title of {}".format(type(title))
        self.__title = title

    @property
    def update_on(self) -> tuple:
        return self.__update_on

    @update_on.setter
    def update_on(self, update_on):
        assert type(update_on) in [list, tuple, str, type(None)], "Unexpected type for update_on of {}".format(type(update_on))
        
        if type(update_on) is list:
            update_on = tuple(update_on)

        elif type(update_on) is str:
            update_on = (update_on,)

        elif update_on is None:
            update_on = tuple()
        
        self.__update_on = update_on

    @property
    def text(self):
        """str: The text of the box."""
        return self.__text

    @text.setter
    def text(self, text):
        self._update_box_text(text)
        self.__text = text
