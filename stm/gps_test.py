import unittest
import gps

class TestMotecLog(unittest.TestCase):

    def test_croft(self):

        latmid = 54.45549431716457
        longmid = -1.5555924154749705

        lat, long = gps.convert(x=0, z=0, latmid=latmid, longmid=longmid)

        self.assertEqual(lat, latmid)
        self.assertEqual(long, longmid)


    def test_croft_east(self):


        # 54.45542226228547, -1.5547022498076541
        #54.45542226228547,-1.5540505807234277

        latmid = 54.45549431716457
        longmid = -1.5555924154749705

        lat, long = gps.convert(x=100, z=0, latmid=latmid, longmid=longmid)

        self.assertEqual(lat, latmid)
        self.assertEqual(long, -1.5540505807234277)


    def test_croft_north(self):


        # 54.456392681105186, -1.5555924154749705

        latmid = 54.45549431716457
        longmid = -1.5555924154749705

        lat, long = gps.convert(x=0, z=100, latmid=latmid, longmid=longmid)

        self.assertEqual(lat, 54.456392681105186)
        self.assertEqual(long, longmid)


if __name__ == '__main__':
    unittest.main()