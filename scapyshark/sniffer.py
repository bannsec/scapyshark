
import scapy.all
from threading import Thread

class Sniffer(object):
    """ Handle sniffing (and effectively reading pcaps) """

    def __init__(self, shark):
        """
        Args:
            shark (scapyshark.ScapyShark): The current scapyshark instance.
        """

        self._shark = shark
        
    def start(self):
        """ Start sniffing. """
        sniffer = Thread(target=scapy.all.sniff, kwargs={'store': False, 'prn': self._handle_new_packet})
        sniffer.daemon = True
        sniffer.start()

    def _handle_new_packet(self, packet):
        self._shark._top_box.add(packet.summary())
        self._shark.loop.draw_screen()
