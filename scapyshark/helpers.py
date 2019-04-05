
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

def update_popup_box_text(box, new_string):

    i = 0
    current_len = len(list(box.body))

    for line in new_string.split('\n'):
        
        new_line = urwid.Text(line)

        # Attempting to utilizing the 'smarts' in urwid to only update lines that need to be updated

        # Our new table has more rows than the original
        if i >= current_len:
            box.body.append(new_line)

        # Changed line
        elif new_line != box.body[i]:
            box.body[i] = new_line

        # Line must be the same as old line
        i += 1

    # Remove any excess lines
    del box.body[i:]

def update_windows(*args, **kwargs):
    import IPython
    IPython.embed()
    exit(0)

import urwid
