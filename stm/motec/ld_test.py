import unittest

from motec import MotecLog

class TestMotecLog(unittest.TestCase):

    def test_create(self):

        log = MotecLog({
            "id": 0x40
        })
        self.assertIsInstance(log, MotecLog, "should be an instance of MotecLog")
        self.assertEqual(log.id, 0x40, "should have assigned the correct")

if __name__ == '__main__':
    unittest.main()
