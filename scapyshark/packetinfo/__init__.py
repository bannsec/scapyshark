
def show_packet_info(scapyshark, packet):
    """ Determine what to display about the given packet and display it. """

    # Grab the actual packet
    packet = scapyshark._top_box.get_packet(packet)
    
    scapyshark._middle_box.base_widget.body.clear()

    for line in packet.show(dump=True).split("\n"):
        scapyshark._middle_box.base_widget.body.append(urwid.Text(line))

import urwid
