import unittest
import os

PATH=os.path.dirname(__file__)

from stm.gt7.packet import GT7DataPacket

class TestGT7Packet(unittest.TestCase):

    def test_idle_status(self):
        with open(os.path.join(PATH, "test", "gt7_idle.bin"), "rb") as fin:

            pkt = GT7DataPacket(fin.read())
            self.assertEqual(pkt.position.x, 0)

    def test_car_code(self):
        with open(os.path.join(PATH, "test", "barcelonagp911.bin"), "rb") as fin:

            pkt = GT7DataPacket(fin.read())
            self.assertEqual(pkt.car_code, 3358, "should decode the correct car code")

    def test_gear(self):
        with open(os.path.join(PATH, "test", "barcelonagp911.bin"), "rb") as fin:

            pkt = GT7DataPacket(fin.read())
            self.assertEqual(pkt.gear, 4, "should decode the correct gear")
            self.assertEqual(pkt.suggested_gear, 2, "should decode the correct suggested gear")

    def test_paused_barcelona(self):
        with open(os.path.join(PATH, "test", "barcelonagp911.bin"), "rb") as fin:

            pkt = GT7DataPacket(fin.read())
            self.assertEqual(pkt.paused, False, "should not decode paused")
            self.assertEqual(pkt.in_race, True, "should decode inrace")

    def test_paused_idle(self):
        with open(os.path.join(PATH, "test", "gt7_idle.bin"), "rb") as fin:

            pkt = GT7DataPacket(fin.read())
            self.assertEqual(pkt.paused, False, "should not decode paused")
            self.assertEqual(pkt.in_race, False, "should decode inrace")

    def test_oil_pressure(self):
        with open(os.path.join(PATH, "test", "barcelonagp911.bin"), "rb") as fin:

            pkt = GT7DataPacket(fin.read())
            expected = 6.866572856903076
            self.assertEqual(pkt.oil_pressure, expected)

    def test_oil_temp(self):
        with open(os.path.join(PATH, "test", "barcelonagp911.bin"), "rb") as fin:

            pkt = GT7DataPacket(fin.read())
            expected = 110.0
            self.assertEqual(pkt.oil_temp, expected)

if __name__ == '__main__':
    unittest.main()