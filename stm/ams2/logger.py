from stm.logger import BaseLogger
from stm.event import STMEvent
import stm.gps as gps
from .shmem import AMS2SharedMemory, AMS2GameState, AMS2RaceState, AMS2SessionState
from datetime import datetime
from logging import getLogger
l = getLogger(__name__)

class AMS2Logger(BaseLogger):

    channels = ['gear', 'throttle', 'brake', 'steer', 'speed', 'lat', 'long']

    def __init__(self, 
                sampler=None,
                filetemplate=None):
        
        super().__init__(sampler=sampler, filetemplate=filetemplate, freq=sampler.freq)

        self.last_lap = None
        self.last_session = None
        self.lap_samples = 0

    def process_sample(self, timestamp, sample):

        new_log = False

        p = AMS2SharedMemory(sample)

        # check we are playing
        if AMS2GameState(p.mGameState) != AMS2GameState.INGAME_PLAYING:
            self.last_lap = None
            return
        
        # check if we are on the track
        if AMS2RaceState(p.mRaceState) != AMS2RaceState.RACING:
            self.last_lap = None
            return

        # get the first participant (us)
        if not len(p.participants):
            return

        driver = p.participants[0]

        if self.last_lap is None:
            self.lap_samples = 0
            self.last_lap = driver.mCurrentLap
            new_log = True

        if self.last_session is None:
            self.last_session = p.mSessionState

        if self.last_session != p.mSessionState:
            new_log = True

        if new_log:
            then = datetime.fromtimestamp(timestamp)
            event = STMEvent(
                date=then.strftime('%d/%m/%Y'),
                time=then.strftime('%H:%M:%S'),
                session=AMS2SessionState(p.mSessionState).name.title(),
                vehicle=p.mCarName,
                driver=driver.mName,
                venue=p.mTrackVariation
            )
            self.new_log(event=event, channels=self.channels)

        if driver.mCurrentLap != self.last_lap:
            # figure out the laptimes
            if p.mLastLapTime > 0:
                laptime = p.mLastLapTime
            else:
                # guess it from the number of samples
                laptime = self.lap_samples / self.freq

            self.add_lap(laptime)
            l.info(f"adding lap {self.last_lap}, laptime: {laptime:.3f}, samples: {self.lap_samples}")
            self.lap_samples = 0
        else:
            self.lap_samples += 1

        self.last_lap = driver.mCurrentLap
        self.last_session = p.mSessionState

        # gear, throttle, brake, speed, z, x
        lat, long = gps.convert(x=-driver.mWorldPositionX, z=-driver.mWorldPositionZ)

        self.add_samples([
            p.mGear,
            p.mThrottle * 100,
            p.mBrake * 100,
            p.mSteering,
            p.mSpeed * 2.23693629, # m/s to mph
            lat,
            long
        ])


