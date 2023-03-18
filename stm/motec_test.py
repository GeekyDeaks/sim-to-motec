import unittest

from motec import MotecByteArray

class TestMotecByteArray(unittest.TestCase):

    def test_create(self):

        ba = MotecByteArray(b"1234")
        self.assertEqual(b"1234", ba.buffer)

    def test_extend(self):
        ba = MotecByteArray()
        ba.update(2, b"1234")
        self.assertEqual(b"\x00\x001234", ba.buffer)

    def test_update(self):
        ba = MotecByteArray(b"0123456789")
        ba.update(4, b"XY")
        self.assertEqual(b"0123XY6789", ba.buffer)


if __name__ == '__main__':
    unittest.main()
