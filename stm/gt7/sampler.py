from stm.sampler import BaseSampler
import socket
import time

DEFAULT_PORT = 33740
DEFAULT_HEARTBEAT_PORT = 33739
PACKETSIZE = 1500

class GT7Sampler(BaseSampler):

    def __init__(self, addr=None, port=DEFAULT_PORT, hb_port=DEFAULT_HEARTBEAT_PORT, rawfile=None):
        super().__init__(rawfile=rawfile)
        self.hb_addr = (addr, hb_port)

        # Create a UDP socket for the inbound packets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to any address
        self.socket.bind( ('0.0.0.0', port) )
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
        send_data = b'A'
        self.socket.sendto(send_data, self.hb_addr)

