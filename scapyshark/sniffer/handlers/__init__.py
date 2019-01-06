
import logging
logger = logging.getLogger('ScapyShark:Sniffer:Handlers')

from . import PcapList
from . import PcapSummary
from . import DNS

# Handlers to run in order on the new packet
handlers = ( 
        PcapList.handle,
        PcapSummary.handle,
        )

def run_all_handlers(sniffer, packet):
    for handler in handlers:
        handler(sniffer, packet)
