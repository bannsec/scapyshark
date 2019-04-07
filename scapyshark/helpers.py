
def iter_layers_by_type(packet, target_type, allow_subclass=False):

    # Scapy doesn't handle iterators very well...
    i = 0

    if target_type not in packet:
        raise StopIteration

    while True:

        try:
            curr = packet[i]
        except IndexError:
            raise StopIteration

        if allow_subclass and isinstance(curr, target_type):
            yield curr

        elif not allow_subclass and type(curr) == target_type:
            yield curr

        i += 1

def sanitize_filename(filename):
    """Take unknown input and sanitize for filename."""

    allowed = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ _-:'
    return ''.join(c for c in filename if c in allowed)

import urwid
