import unittest

import stm.ams2.convert as c
from stm.maths import Vector
import math

class TestAMS2SharedMemory(unittest.TestCase):


    def test_orientation(self):

        values = [
            ( Vector(0, math.pi, 0), Vector(0, 0, 0) ),
            ( Vector(0, math.pi/2, 0), Vector(0, -90, 0) ),
            ( Vector(0, -math.pi/2, 0), Vector(0, 90, 0) ),
            ( Vector(0, 0, 0), Vector(0, -180, 0) ),
            ( Vector(0, -math.pi, 0), Vector(0, 0, 0) ),
            ( Vector(0, -math.pi/4, 0), Vector(0, 135, 0) ),
            ( Vector(0, -math.pi*3/4, 0), Vector(0, 45, 0) ),

            ( Vector(0, math.pi/4, 0), Vector(0, -135, 0) ),
            ( Vector(0, math.pi*3/4, 0), Vector(0, -45, 0) ),

        ]

        for v, expected in values:

            r = c.convert_orientation(v)
            self.assertEqual(expected, r)


if __name__ == '__main__':
    unittest.main()