import unittest

from stm.ams2.tracks import lookup_track

class TestTracks(unittest.TestCase):

    def test_lookup(self):
        track = lookup_track("Bathurst_1983")
        self.assertEqual(track.refLat, -33.448739, "should have the correctl refLat")


    def test_nolookup(self):
        track = lookup_track("Unknown")
        self.assertIsNone(track, "should return None")


    def test_convert_to_gps(self):
        track = lookup_track("Bathurst_1983")
        lat, long = track.convert_to_gps(1, 1)
        self.assertEqual(lat, -33.44872975501888, "should convert to the correct lat")
        self.assertEqual(long, 149.54618048630493, "should convert to the correct long")
    

if __name__ == '__main__':
    unittest.main()