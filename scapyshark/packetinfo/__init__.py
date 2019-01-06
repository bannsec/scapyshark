
def show_packet_info(scapyshark, packet):
    """ Determine what to display about the given packet and display it. """

    # Grab the actual packet
    packet = scapyshark._top_box.get_packet(packet)

    #
    # Middle Box
    #
    
    scapyshark._middle_box.base_widget.body.clear()

    for line in packet.show(dump=True).split("\n"):
        scapyshark._middle_box.base_widget.body.append(urwid.Text(line))

    #
    # Bottom Box
    #

    scapyshark._bottom_box.base_widget.body.clear()

    b = bytes(packet)
    first_line = 0

    for i in range(0, len(b), 16):
        b_chunk = b[i:i+16]

        line = ":".join("{:02x}".format(c) for c in b_chunk)

        if first_line == 0:
            first_line = len(line)
        else:
            if len(line) != first_line:
                line += ' '*(first_line - len(line))

        line += ' | '

        for c in b_chunk:
            c2 = chr(c)
            if c2 in printable:
                line += c2
            else:
                line += '.'

        scapyshark._bottom_box.base_widget.body.append(urwid.Text(line))

printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '

import urwid
