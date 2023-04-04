from stm.logger import BaseLogger
from stm.event import STMEvent
import stm.gps as gps
from .shmem import AMS2SharedMemory, AMS2GameState, AMS2RaceState, AMS2SessionState
from datetime import datetime
from logging import getLogger
l = getLogger(__name__)

class AMS2Logger(BaseLogger):

    channels = ['beacon', 'lap', 'rpm', 'gear', 'throttle', 'brake', 'steer', 'speed', 'lat', 'long',
                'glat', 'gvert', 'glong']

    def __init__(self,
                rawfile=None,
                sampler=None,
                filetemplate=None):
        
        super().__init__(rawfile=rawfile, sampler=sampler, filetemplate=filetemplate)

        self.last_packet = None
        self.lap_samples = 0

    def process_sample(self, timestamp, sample):

        p = AMS2SharedMemory(sample)
        if not self.last_packet:
            self.last_packet = p

        self.process_packet(timestamp, p, self.last_packet)
        self.last_packet = p

    def process_packet(self, timestamp, p, lastp):

        new_log = False
        freq = self.sampler.freq
        beacon = 0

        # check we are playing
        if AMS2GameState(p.mGameState) != AMS2GameState.INGAME_PLAYING:
            self.save_log()
            return
        
        # check if we are on the track
        if AMS2RaceState(p.mRaceState) != AMS2RaceState.RACING:
            self.save_log()
            return

        # get the first participant (us)
        if not len(p.participants):
            return

        if lastp.mSessionState != p.mSessionState:
            l.info("new session state: " + AMS2SessionState(p.mSessionState).name)
            self.save_log()

        if not self.log:
            then = datetime.fromtimestamp(timestamp)
            event = STMEvent(
                date=then.strftime('%d/%m/%Y'),
                time=then.strftime('%H:%M:%S'),
                session=AMS2SessionState(p.mSessionState).name.title(),
                vehicle=p.mCarName,
                driver=p.driver.mName,
                venue=p.mTrackVariation
            )
            self.new_log(event=event, channels=self.channels)

        if p.driver.mCurrentLap > lastp.driver.mCurrentLap:
            # figure out the laptimes
            if p.mLastLapTime > 0:
                laptime = p.mLastLapTime
            else:
                # guess it from the number of samples
                laptime = self.lap_samples / freq

            self.add_lap(laptime)
            l.info(f"adding lap {self.last_lap}, laptime: {laptime:.3f}, samples: {self.lap_samples}")
            self.lap_samples = 0
            beacon = 1

        if p.driver.mCurrentSector >= 0 and p.driver.mCurrentSector != lastp.driver.mCurrentSector:
            beacon = p.driver.mCurrentSector + 1
            
        self.lap_samples += 1

        self.last_lap = p.driver.mCurrentLap
        self.last_session = p.mSessionState

        # gear, throttle, brake, speed, z, x
        lat, long = gps.convert(x=-p.driver.mWorldPosition.x, z=-p.driver.mWorldPosition.z)

        glat, gvert, glong = [ a / 9.8 for a in p.mLocalAcceleration]
        self.add_samples([
            beacon,
            p.driver.mCurrentLap,
            p.mRpm,
            p.mGear,
            p.mThrottle * 100,
            p.mBrake * 100,
            p.mSteering * 50,
            p.mSpeed * 2.23693629, # m/s to mph
            lat,
            long,
            glat,
            gvert,
            -glong
        ])


