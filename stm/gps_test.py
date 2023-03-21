import unittest
import gps

class TestGPS(unittest.TestCase):

    def test_croft(self):

        latmid = 54.45549431716457
        longmid = -1.5555924154749705

        lat, long = gps.convert(x=0, z=0, latmid=latmid, longmid=longmid)

        self.assertEqual(lat, latmid)
        self.assertEqual(long, longmid)


    def test_croft_east(self):

        latmid = 54.45549431716457
        longmid = -1.5555924154749705

        lat, long = gps.convert(x=100, z=0, latmid=latmid, longmid=longmid)

        self.assertEqual(lat, latmid)
        self.assertEqual(long, -1.5540505807234277)


    def test_croft_north(self):

        latmid = 54.45549431716457
        longmid = -1.5555924154749705

        lat, long = gps.convert(x=0, z=100, latmid=latmid, longmid=longmid)

        self.assertEqual(lat, 54.456392681105186)
        self.assertEqual(long, longmid)


if __name__ == '__main__':
    unittest.main()