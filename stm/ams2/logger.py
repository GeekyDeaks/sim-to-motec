from stm.logger import BaseLogger
from stm.event import STMEvent
import stm.gps as gps
from .shmem import AMS2SharedMemory, AMS2GameState
from datetime import datetime
from logging import getLogger
l = getLogger(__name__)

class AMS2Logger(BaseLogger):

    channels = [
                'beacon', 'br2', # lap or sector points
                'lap', 'rpm', 'gear', 
                'throttle', 'brake', 'steer', 'speed', 
                'lat', 'long',
                'glat', 'gvert', 'glong',  # g forces
                'suspfl', 'suspfr', 'susprl', 'susprr', # suspension travel
                'suspvelfl', 'suspvelfr', 'suspvelrl', 'suspvelrr', # suspension velocity
                'tyretempfl', 'tyretempfr', 'tyretemprl', 'tyretemprr', # combined tyre temp
                'braketempfl', 'braketempfr', 'braketemprl', 'braketemprr', # brake temp
                'tyretempflo', 'tyretempfro', # outer temp
                'tyretempflc', 'tyretempfrc', # center temp
                'tyretempfli', 'tyretempfri', # inner temp
                #'wheelslipfl', 'wheelslipfr', 'wheelsliprl', 'wheelsliprr', # wheel slip
                'rideheightfl', 'rideheightfr', 'rideheightrl', 'rideheightrr', 
                'tyrepresfl', 'tyrepresfr', 'tyrepresrl', 'tyrepresrr', # mAirPressure
                'turbopres',
                'brakebias',
                'enginetorque',
                'lap', 'laptime',
                'racestate', # AMS2 race status
                ]

    def __init__(self,
                rawfile=None,
                sampler=None,
                filetemplate=None):
        
        super().__init__(rawfile=rawfile, sampler=sampler, filetemplate=filetemplate)

        self.last_packet = None

    def process_sample(self, timestamp, sample):

        p = AMS2SharedMemory(sample)
        if not self.last_packet:
            self.last_packet = p

        self.process_packet(timestamp, p, self.last_packet)
        self.last_packet = p

    def process_packet(self, timestamp, p, lastp):

        freq = self.sampler.freq
        br2 = 0

        if p.mGameState == AMS2GameState.INGAME_PAUSED:
            return

        # check we are playing
        if p.mGameState != AMS2GameState.INGAME_PLAYING:
            self.save_log()
            return

        # get the first participant (us)
        if not len(p.participants):
            return

        if lastp.mSessionState != p.mSessionState:
            l.info("new session state: " + p.mSessionState.name)
            self.save_log()

        if not self.log:
            then = datetime.fromtimestamp(timestamp)
            event = STMEvent(
                datetime=then.strftime("%Y-%m-%dT%H:%M:%S"),
                session=p.mSessionState.name.title(),
                vehicle=p.mCarName,
                driver=p.driver.mName,
                venue=p.mTrackVariation
            )
            self.new_log(event=event, channels=self.channels)

        if p.driver.mCurrentLap > lastp.driver.mCurrentLap or p.driver.mCurrentSector < lastp.driver.mCurrentSector:
            self.add_lap(laptime=p.mLastLapTime, lap=lastp.driver.mCurrentLap)

        if p.driver.mCurrentSector >= 0 and p.driver.mCurrentSector != lastp.driver.mCurrentSector:
            br2 = p.driver.mCurrentSector + 1
            l.info(f"{self.lap_samples}, setting beacon {br2} as moving from sector {lastp.driver.mCurrentSector} to {p.driver.mCurrentSector}")

        # gear, throttle, brake, speed, z, x
        lat, long = gps.convert(x=-p.driver.mWorldPosition.x, z=-p.driver.mWorldPosition.z)

        glat, gvert, glong = [ a / 9.8 for a in p.mLocalAcceleration]
        self.add_samples([
            1 if br2 > 0 else 0,
            br2,
            p.driver.mCurrentLap,
            p.mRpm,
            p.mGear,
            p.mThrottle * 100,
            p.mBrake * 100,
            p.mSteering * 40, # arbitratry scale based on some testing
            p.mSpeed * 2.23693629, # m/s to mph
            lat,
            long,
            glat,
            gvert,
            -glong,
            *[sp * 100 for sp in p.mSuspensionTravel],
            *p.mSuspensionVelocity,
            *p.mTyreTemp,
            *p.mBrakeTempCelsius,
            p.mTyreTempLeft.fl, p.mTyreTempRight.fr,     # outer
            p.mTyreTempCenter.fl, p.mTyreTempCenter.fr, # centre
            p.mTyreTempRight.fl, p.mTyreTempLeft.fr,   # inner
            #*[s * 2.23693629 for s in p.mTyreSlipSpeed], # wheel slip m/s -> mph
            *p.mRideHeight,
            *p.mAirPressure,
            p.mTurboBoostPressure,
            p.mBrakeBias,
            p.mEngineTorque,
            p.driver.mCurrentLap,
            p.mCurrentTime,
            p.mRaceState.value,
        ])


