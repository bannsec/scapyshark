
import scapy
import urwid

def handle(sniffer, packet):
    global count_tcp, count_udp, count_arp, count_other

    if packet.haslayer(scapy.layers.inet.TCP):
        count_tcp += 1

    elif packet.haslayer(scapy.layers.inet.UDP):
        count_udp += 1

    elif packet.haslayer(scapy.layers.inet.ARP):
        count_arp += 1

    else:
        count_other += 1

    footer_text = 'TCP: {}, UDP: {}, ARP: {}, Other: {}'.format(count_tcp, count_udp, count_arp, count_other)

    footer = sniffer._shark._footer_box.base_widget
    footer.set_text(footer_text)

try:
    count_tcp
except:
    count_tcp = 0
    count_udp = 0
    count_arp = 0
    count_other = 0
