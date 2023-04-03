import unittest
from .quaternion import Quaternion
from .vector import Vector

class TestVector(unittest.TestCase):

    def test_mult_Quaternion(self):

        v1 = Vector(1, 0, 0)
        q1 = Quaternion(0.707, 0.0,  0.707, 0.0)
        vactual = v1 * q1
        vexpect = Vector(0, 0, -1)

        for a,b  in zip(vactual, vexpect):
            self.assertAlmostEqual(a, b, places=3)


    def test_subtract(self):
        v1 = Vector(1, 0, 0)
        v2 = Vector(2, 1, 0)

        vactual = v1 - v2
        vexpect = Vector(-1, -1, 0)

        self.assertEqual(vactual, vexpect)

if __name__ == '__main__':
    unittest.main()