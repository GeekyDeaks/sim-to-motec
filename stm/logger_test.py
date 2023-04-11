import unittest

from stm.logger import BaseLogger
from stm.event import  STMEvent
import os


class TestBaseLogger(unittest.TestCase):

    def test_new_log(self):

        event = STMEvent(driver="Steve McQueen")
        l = BaseLogger(filetemplate="{driver}")
        l.new_log(event=event, channels=[])
        self.assertEqual(l.filename, "Steve_McQueen")

    def test_valid_filename(self):

        event = STMEvent(driver="Steve:McQueen", datetime="2021-12-01")
        l = BaseLogger(filetemplate=os.path.join("a", "b", "{driver}_{vehicle}_{datetime}") )
        l.new_log(event=event, channels=[])
        expected = os.path.join("a", "b", "SteveMcQueen_2021-12-01")
        self.assertEqual(l.filename, expected)

    def test_remove_dir(self):
    
        event = STMEvent(driver="Steve:McQueen", datetime="2021-12-01")
        l = BaseLogger(filetemplate=os.path.join("a", "{vehicle}", "{driver}_{vehicle}_{datetime}") )
        l.new_log(event=event, channels=[])
        expected = os.path.join("a", "SteveMcQueen_2021-12-01")
        self.assertEqual(l.filename, expected)

    def test_remove_trailing_underscore(self):
    
        event = STMEvent(driver="Steve:McQueen", datetime="2021-12-01")
        l = BaseLogger(filetemplate=os.path.join("a", "b", "{driver}_{datetime}_{vehicle}") )
        l.new_log(event=event, channels=[])
        expected = os.path.join("a", "b", "SteveMcQueen_2021-12-01")
        self.assertEqual(l.filename, expected)

    def test_remove_leading_underscore(self):
    
        event = STMEvent(driver="Steve:McQueen", datetime="2021-12-01")
        l = BaseLogger(filetemplate=os.path.join("a", "b", "{vehicle}_{driver}_{datetime}") )
        l.new_log(event=event, channels=[])
        expected = os.path.join("a", "b", "SteveMcQueen_2021-12-01")
        self.assertEqual(l.filename, expected)

if __name__ == '__main__':
    unittest.main()