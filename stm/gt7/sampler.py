from stm.sampler import BaseSampler
import socket
import time
from logging import getLogger
l = getLogger(__name__)

DEFAULT_PORT = 33740
DEFAULT_HEARTBEAT_PORT = 33739
PACKETSIZE = 1500

class GT7Sampler(BaseSampler):

    def __init__(self, addr=None, port=DEFAULT_PORT, hb_port=DEFAULT_HEARTBEAT_PORT, freq=None):
        super().__init__(freq=freq)
        if port != DEFAULT_PORT:
            # do not send heartbeats if we are not running on the default ports
            # as GT7 will ignore them anyway
            self.hb_addr = None
            l.info("Relay mode.  Not sending heartbeat packets to GT7")
        else:
            self.hb_addr = (addr, hb_port)

        # Create a UDP socket for the inbound packets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to any address
        self.socket.bind( ('0.0.0.0', int(port)) )
        self.socket.settimeout(1)

    def run(self):

        self.running = True # this is set to False in BaseSampler when we are done
        #
        self.send_hb()
        pkt_count = 0

        while self.running:
            try:

                data, _ = self.socket.recvfrom(PACKETSIZE)
                ts = time.time()
                pkt_count += 1

                if (pkt_count % 100) == 0:
                    # send a heartbeat about every 6 seconds
                    self.send_hb()


                self.put((ts, data))

            except socket.timeout:
                self.send_hb()


    def send_hb(self):
        if not self.hb_addr:
            return
        
        send_data = b'A'
        try:
            self.socket.sendto(send_data, self.hb_addr)
        except Exception as e:
            #l.error(e)
            pass

