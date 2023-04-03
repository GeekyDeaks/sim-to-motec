import unittest
from .quarternion import Quarternion

class TestQuarternion(unittest.TestCase):

    def test_mult(self):

        q1 = Quarternion(0.53767, 0.31877, 3.5784, 0.7254)
        q2 = Quarternion(-0.12414, 1.4897, 1.409, 1.4172)

        q3 = q1 * q2

        qexpect = Quarternion(-6.6117, 4.8105, 0.94224, -4.2097)
        for a,b  in zip(q3, qexpect):
            self.assertAlmostEqual(a, b, places=3)

    def test_mult2(self):

        q1 = Quarternion(1.8339, -1.3077, 2.7694, -0.063055)
        q2 = Quarternion(-0.12414, 1.4897, 1.409, 1.4172)

        q3 = q1 * q2

        qexpect = Quarternion(-2.0925, 6.9079, 3.9995, -3.3614)
        for a,b  in zip(q3, qexpect):
            self.assertAlmostEqual(a, b, places=3)


if __name__ == '__main__':
    unittest.main()