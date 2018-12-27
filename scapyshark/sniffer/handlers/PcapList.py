
def handle(sniffer, packet):
    sniffer._shark._top_box.add(packet.summary(), packet)
