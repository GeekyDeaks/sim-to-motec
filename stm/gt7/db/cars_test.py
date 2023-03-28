import unittest

from .cars import lookup_car_name

class TestGTCarsDB(unittest.TestCase):

    def test_porsche(self):
        name = lookup_car_name(3358)
        # 3358,911 GT3 (996) '01,136
        self.assertEqual(name, "911 GT3 (996) '01", "should find the porsche")

if __name__ == '__main__':
    unittest.main()