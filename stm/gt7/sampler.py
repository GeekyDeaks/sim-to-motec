from threading import Thread
import socket
import time
from queue import Queue
from .packet import GT7DataPacket

DEFAULT_PORT = 33740
DEFAULT_HEARTBEAT_PORT = 33739

class GT7Sampler(Thread):

    def __init__(self, addr=None, port=DEFAULT_PORT, hb_port=DEFAULT_HEARTBEAT_PORT):
        super().__init__()
        self.hb_addr = (addr, hb_port)
        self.running = False

        # Create a UDP socket for the inbound packets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to any address
        self.socket.bind( ('0.0.0.0', port) )
        self.socket.settimeout(1)
        self.samples = Queue()

    def run(self):

        self.running = True
        #
        self.send_hb()
        pkt_count = 0

        while self.running:
            try:

                data, _ = self.socket.recvfrom(GT7DataPacket.size)
                ts = time.time()
                pkt_count += 1

                if (pkt_count % 100) == 0:
                    # send a heartbeat about every 6 seconds
                    self.send_hb()

                p = GT7DataPacket(data)
                self.samples.put((ts, p), block=False)

            except TimeoutError:
                self.send_hb()

    def send_hb(self):
        send_data = b'A'
        self.socket.sendto(send_data, self.hb_addr)

    def stop(self):
        self.running = False

    def get(self, timeout=None):
        return self.samples.get(timeout=timeout)
