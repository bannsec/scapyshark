

def build_menu(scapyshark):
    global menu
    global packets

    # TODO: This is hack so that I can retain access to the sniffer object...
    try:
        packets
    except:
        packets = scapyshark._top_box.packets

    #
    # Write to PCAP Dialogue
    #

    edit = {
        'caption': 'Output File: ',
        'edit_text': 'output.pcap',
        'multiline': True,
        'align': 'left',
        'allow_tab': False,
    }

    buttons = []
    buttons.append(urwid.Button('Save', on_press=save_to_pcap_button_handler, user_data=scapyshark))
    buttons.append(urwid.Button('Cancel', on_press= lambda _: scapyshark._pop_overlay()))

    write_to_pcap_dialogue = lambda: scapyshark._dialogue_general('', title='Write to PCAP', edit=edit, buttons=buttons, edit_enter_handler=save_to_pcap_handler)

    menu_items = [
        ('Write to pcap', write_to_pcap_dialogue),
        ('Close', scapyshark._pop_overlay)
    ]

    menu = MenuBase(scapyshark, title='Files', menu_items=menu_items)
    return menu

#
# Save to PCAP
#

def save_to_pcap_handler(file_name):
    file_name = os.path.abspath(file_name)
    scapy.all.wrpcap(file_name, packets, gz=False)

def save_to_pcap_button_handler(button, scapyshark):
    edit_text = scapyshark._dialogue_general_get_edit_text()

    # Done with this dialogue, remove it
    scapyshark._pop_overlay()

    save_to_pcap_handler(edit_text)


import os
import scapy.all
import urwid
from . import MenuBase
