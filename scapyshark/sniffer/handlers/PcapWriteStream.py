
import os
import scapy.utils
import urwid

def handle(sniffer, packet):
    global write_path, write_object

    # We're not stream writing
    if write_path is False:
        return
    
    # We haven't figured out if we should be writing or not
    elif write_path is None:

        # We're not going to be streaming
        if sniffer._write_stream is False:
            write_path = False
            return

        # We're going to be streaming, setup for it
        write_path = os.path.abspath(sniffer._write_stream)
        write_object = scapy.utils.PcapWriter(write_path, gz=False)

    # Time to write
    if write_object is not None:
        # TODO: Flushing each packet might become an issue at larger traffic volumes...
        write_object.write(packet)
        write_object.flush()

try:
    write_path
except:
    write_path = None
    write_object = None
