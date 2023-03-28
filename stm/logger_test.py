import unittest

from stm.logger import BaseLogger
from stm.event import  STMEvent


class TestBaseLogger(unittest.TestCase):

    def test_new_log(self):

        event = STMEvent(driver="Steve McQueen")
        l = BaseLogger(filetemplate="{driver}")
        l.new_log(event=event, channels=[])
        self.assertEqual(l.filename, "Steve_McQueen")

    def test_valid_filename(self):

        event = STMEvent(driver="Steve:McQueen", date="10/01/2021")
        l = BaseLogger(filetemplate="a/b/{driver}_{vehicle}_{date}")
        l.new_log(event=event, channels=[])
        self.assertEqual(l.filename, "a/b/SteveMcQueen_10012021")

if __name__ == '__main__':
    unittest.main()