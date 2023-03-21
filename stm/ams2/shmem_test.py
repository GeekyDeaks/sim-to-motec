import unittest
import os

PATH=os.path.dirname(__file__)

from stm.ams2.shmem import AMS2SharedMemory

class TestAMS2SharedMemory(unittest.TestCase):


    def test_idle_status(self):
        with open(os.path.join(PATH, "test", "ams2_idle.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            self.assertEqual(sm.mVersion, 13)



    def test_inrace_participants(self):
        with open(os.path.join(PATH, "test", "ams2_inrace.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            self.assertEqual(sm.mVersion, 13)
            self.assertEqual(sm.mNumParticipants, 21)
            self.assertEqual(len(sm.participants), 21)

            self.assertEqual(sm.participants[0].mName , "Scott Deakin")
            self.assertEqual(sm.participants[20].mName , "Bill Elliott")


if __name__ == '__main__':
    unittest.main()