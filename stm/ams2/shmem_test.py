import unittest
import os
from stm.ams2.shmem import Wheels

PATH=os.path.dirname(__file__)

from stm.ams2.shmem import AMS2SharedMemory

class TestAMS2SharedMemory(unittest.TestCase):


    def test_idle_status(self):
        with open(os.path.join(PATH, "test", "ams2_idle.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            self.assertEqual(sm.mVersion, 13)


    def test_idle_alignment_padding(self):
        with open(os.path.join(PATH, "test", "ams2_idle.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            # check values after variables that tend to break alignment e.g. boolean
            self.assertEqual(sm.mBestLapTime, -1.0)
            self.assertEqual(sm.mLastLapTime, -1.0)

    def test_inrace_participants(self):
        with open(os.path.join(PATH, "test", "ams2_inrace.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            self.assertEqual(sm.mVersion, 13)
            self.assertEqual(sm.mNumParticipants, 21)
            self.assertEqual(len(sm.participants), 21)

            self.assertEqual(sm.participants[0].mName , "Scott Deakin")
            self.assertEqual(sm.participants[20].mName , "Bill Elliott")


    def test_inrace_driver_x(self):
        with open(os.path.join(PATH, "test", "ams2_inrace.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            self.assertEqual(sm.mVersion, 13)
            self.assertEqual(sm.driver.mWorldPosition.x , 1406.681396484375)

    def test_inrace_controls(self):
        with open(os.path.join(PATH, "test", "ams2_inrace.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            self.assertEqual(sm.mGear, 0)
            self.assertEqual(sm.mClutch, 1.0)
            self.assertEqual(sm.mThrottle, 0.0)
            self.assertEqual(sm.mBrake, 1.0)


    def test_local_accel(self):
        with open(os.path.join(PATH, "test", "ams2_inrace.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            self.assertAlmostEqual(sm.mLocalAcceleration.x, -0.0003, places=4)

    def test_inrace_suspension(self):
        with open(os.path.join(PATH, "test", "ams2_inrace.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            expected  = Wheels(0.07931163161993027, 0.08020654320716858, 
                               0.08346261084079742, 0.08160709589719772)
            self.assertEqual(sm.mSuspensionTravel, expected)

    def test_inrace_braketemp(self):
        with open(os.path.join(PATH, "test", "ams2_inrace.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            expected  = Wheels(121.34285736083984, 121.34252166748047, 
                               121.5243148803711, 121.5244140625)
            self.assertEqual(sm.mBrakeTempCelsius, expected)

    def test_inrace_translated(self):
        with open(os.path.join(PATH, "test", "ams2_inrace.bin"), "rb") as fin:

            sm = AMS2SharedMemory(fin.read())
            expected = "Bathurst"
            self.assertEqual(sm.mTranslatedTrackLocation, expected)

if __name__ == '__main__':
    unittest.main()