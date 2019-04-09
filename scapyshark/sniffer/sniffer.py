
import logging
logger = logging.getLogger('ScapyShark:Sniffer')

import scapy.all
from threading import Thread
import pexpect
import atexit
import os
import struct
from time import time, sleep
import json
import collections
import shutil
import subprocess
import random
import multiprocessing
import itertools
import psutil

TSHARK_PIPE = '/tmp/scapyshark.pipe'

class Sniffer(object):
    """ Handle sniffing (and effectively reading pcaps) """

    def __init__(self, shark):
        """
        Args:
            shark (scapyshark.ScapyShark): The current scapyshark instance.
        """

        self._shark = shark

        # Should we be streaming pcap write to file and, if so, where
        self._write_stream = shark._args.w
        self._read_pcap = shark._args.r
        self._max_count = shark._args.c
        self._timeout = shark._args.t

        if shutil.which('tshark') is None:
            logger.warn('tshark is not installed. No enrichment will be done.')
            self._notshark = True
        else:
            self._init_tshark()
            self._notshark = False

        # Channel hop will be it's own process
        if shark._args.channel_hop is not None:
            p = multiprocessing.Process(target=self._start_channel_hop, args=[shark._args.channel_hop])
            p.daemon = True
            p.start()
        
    def start(self):
        """ Start sniffing. """
        lfilter = None
        if self._shark._args.lfilter is not None:
            lfilter = lambda packet: eval(self._shark._args.lfilter)

        # iface is supposed to sniff on all interfaces but sometimes it doesn't... Explicitly identifying interfaces with psutil.
        kwargs={'store': False,
                'prn': self._handle_new_packet,
                'filter': ' '.join(self._shark._args.expression),
                'offline': self._read_pcap,
                'count': self._max_count,
                'timeout': self._timeout,
                'lfilter': lfilter,
                'iface': [nic for nic, val in psutil.net_if_stats().items() if val.isup]
                }

        sniffer = Thread(target=scapy.all.sniff, kwargs=kwargs)
        sniffer.daemon = True
        sniffer.start()

    def _start_channel_hop(self, interface):
        # TODO: Verify interface exists first
        
        channels = list(range(1,13))
        random.shuffle(channels) # Random channel hop order
        channels_cycle = itertools.cycle(channels)

        while True:
            channel = next(channels_cycle)
            # TODO: Check if we need sudo and only add it if needed.
            subprocess.call(['sudo', 'iwconfig', interface, 'channel', str(channel)]) 
            sleep(0.5)


    def _init_tshark(self):
        """ Setup tshark for parsing more info. """

        # Freshen the pipe
        if os.path.exists(TSHARK_PIPE):
            os.unlink(TSHARK_PIPE)
        os.mkfifo(TSHARK_PIPE)

        #self._tshark = pexpect.spawn('tshark', ['-n','-T','json','-l', '-i', TSHARK_PIPE], echo=False, encoding='utf-8', maxread=20000)
        self._tshark = pexpect.spawn('tshark', ['-n','-T','ek','-l', '-i', TSHARK_PIPE], echo=False, encoding='utf-8', maxread=20000)
        atexit.register(self._tshark.close) 

        # Clear buffer
        self._tshark.expect(['Capturing'])
        self._tshark.expect(['\n'])

        # Basic header
        linktype = 1 # Ethernet TODO: Might have to change this for 802.11 and others...
        global_header = struct.pack("<IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, scapy.all.MTU, 1)

        # Open up the pipe
        self._tshark_pipe = open(TSHARK_PIPE, 'wb')
        self._tshark_pipe.write(global_header)
        self._tshark_pipe.flush()


    def _format_packet(self, packet):
        """ Format the given packet to be streamed into tshark. Return the bytes. """
        assert isinstance(packet, scapy.layers.l2.Ether), "Unexpected packet type of {}".format(type(packet))
        return struct.pack('<I', int(time())) + struct.pack('<I',0) + struct.pack('<I', len(packet)) + struct.pack('<I', len(packet)) + bytes(packet) 

    def _handle_new_packet(self, packet):
        #enriched_data = self._get_packet_enriched_data(packet)
        #self._shark._top_box.add(packet.summary(), packet)
        run_all_handlers(self, packet)
        self._shark.loop.draw_screen()

    def _get_packet_enriched_data(self, packet):
        """ Call out to tshark to get enriched packet data. """

        # If tshark isn't here, we can't enrich
        if self._notshark:
            logger.debug('No tshark. Ignoring request for enriched data.')
            return None
        
        # Write the packet to the pipe
        self._tshark_pipe.write(self._format_packet(packet))
        self._tshark_pipe.flush()

        self._tshark.readline() # This should be the index json line
        b = self._tshark.readline()
        return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(b)

        # Read back input
        #self._tshark.expect(['  \}\r\n'])
        #self._tshark.interact()

        # Get past some json junk..
        self._tshark.expect(['\{'])

        # TODO: Kinda jenky way to figure out this json stream...
        b = '{'
        while True:

            self._tshark.expect(['\}'])
            b += self._tshark.before + self._tshark.after

            try:
                return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(b)
            except Exception as e:
                continue

from .handlers import run_all_handlers
