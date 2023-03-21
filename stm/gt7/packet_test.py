import unittest
import os

PATH=os.path.dirname(__file__)

from stm.gt7.packet import GT7DataPacket

class TestGT7Packet(unittest.TestCase):


    def test_idle_status(self):
        with open(os.path.join(PATH, "test", "gt7_idle.bin"), "rb") as fin:

            pkt = GT7DataPacket(fin.read())
            self.assertEqual(pkt.positionX, 0)


if __name__ == '__main__':
    unittest.main()