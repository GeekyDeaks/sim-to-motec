from struct import Struct
from enum import Enum
from collections import namedtuple
from stm.maths import Vector

Wheels = namedtuple("Wheels", ["fl", "fr", "rl", "rr"])

class AMS2GameState(Enum):
    EXITED = 0
    FRONT_END = 1
    INGAME_PLAYING = 2
    INGAME_PAUSED = 3
    INGAME_INMENU_TIME_TICKING = 4
    INGAME_RESTARTING = 5
    INGAME_REPLAY = 6
    FRONT_END_REPLAY = 7

class AMS2SessionState(Enum):
    INVALID = 0
    PRACTICE = 1
    TEST = 2
    QUALIFY = 3
    FORMATION_LAP = 4
    RACE = 5
    TIME_ATTACK = 6

class AMS2RaceState(Enum):
    INVALID = 0
    NOT_STARTED = 1
    RACING = 2
    FINISHED = 3
    DISQUALIFIED = 4
    RETIRED = 5
    DNF = 6


class AMS2ParticipantInfo:

    fmt = Struct(
        "<"
        "?" # mIsActive
        "64s" # mName (STRING_LENGTH_MAX - 1)
        "3x" # alignment padding
        "3f" # mWorldPosition
        "f" # mCurrentLapDistance
        "I" # mRacePosition
        "I" # mLapsCompleted
        "I" # mCurrentLap
        "i" # mCurrentSector
    )

    def __init__(self, buf):
        (
            self.mIsActive, 
            mName,
            x, y, z,
            self.mCurrentLapDistance,
            self.mRacePosition,
            self.mLapsCompleted,
            self.mCurrentLap,
            self.mCurrentSector

        ) = self.fmt.unpack(buf[:self.fmt.size])

        self.mWorldPosition = Vector(x, y, z)
        self.mName = mName.decode('latin-1').rstrip('\0')

    @property
    def size(self):
        return self.fmt.size


class AMS2SharedMemory:

    fmt = Struct(
        "<"
        "I"     # mVersion
        "I"     # mBuildVersionNumber
        "I"     # mGameState
        "I"     # mSessionState
        "I"     # mRaceState
        "i"     # mViewedParticipantIndex
        "i"     # mNumParticipants
        "6400s" # mParticipantInfo ( STORED_PARTICIPANTS_MAX * AMS2ParticipantInfo.size )
        "f"     # mUnfilteredThrottle
        "f"     # mUnfilteredBrake
        "f"     # mUnfilteredSteering
        "f"     # mUnfilteredClutch
        "64s"   # mCarName
        "64s"   # mCarClassName
        "I"     # mLapsInEvent
        "64s"   # mTrackLocation
        "64s"   # mTrackVariation
        "f"     # mTrackLength
        "i"     # mNumSectors
        "?"     # mLapInvalidated
        "3x"    # alignment padding
        "f"     # mBestLapTime
        "f"     # mLastLapTime
        "f"     # mCurrentTime
        "120x"  # skip a load of stuff we are not currently interested in
        "f"     # mSpeed
        "f"     # mRpm
        "f"     # mMaxRPM
        "f"     # mBrake
        "f"     # mThrottle
        "f"     # mClutch
        "f"     # mSteering
        "i"     # mGear
        "i"     # mNumGears
        "f"     # mOdometerKM
        "?"     # mAntiLockActive
        "3x"    # alignment padding
        "4x"    # mLastOpponentCollisionIndex
        "4x"    # mLastOpponentCollisionMagnitude
        "?"     # mBoostActive
        "3x"    # alignment padding
        "f"     # mBoostAmount
        "3f"    # mOrientation
        "3f"    # mLocalVelocity
        "3f"    # mWorldVelocity
        "3f"    # mAngularVelocity
        "3f"    # mLocalAcceleration
        "12x"   # mWorldAcceleration
        "12x"   # mExtentsCentre
        "16x"   # mTyreFlags
        "16x"   # mTerrain
        "16x"   # mTyreY
        "16x"   # mTyreRPS
        "16x"   # mTyreSlipSpeed
        "4f"    # mTyreTemp
        "16x"   # mTyreGrip
        "16x"   # mTyreHeightAboveGround
        "16x"   # mTyreLateralStiffness
        "16x"   # mTyreWear
        "16x"   # mBrakeDamage
        "16x"   # mSuspensionDamage
        "4f"    # mBrakeTempCelsius
        "16x"   # mTyreTreadTemp
        "16x"   # mTyreLayerTemp
        "16x"   # mTyreCarcassTemp
        "16x"   # mTyreRimTemp
        "16x"   # mTyreInternalAirTemp
        "4x"    # mCrashState / I / 4x
        "4x"    # mAeroDamage
        "4x"    # mEngineDamage
        "4x"    # mAmbientTemperature
        "4x"    # mTrackTemperature
        "4x"    # mRainDensity 
        "4x"    # mWindSpeed
        "4x"    # mWindDirectionX
        "4x"    # mWindDirectionY
        "4x"    # mCloudBrightness
        "4x"    # mSequenceNumber
        "16x"   # mWheelLocalPositionY      
        "4f"    # mSuspensionTravel

    )

    def __init__(self, buf):

        (
            self.mVersion, 
            self.mBuildVersionNumber,
            self.mGameState,
            self.mSessionState,
            self.mRaceState,
            self.mViewedParticipantIndex,
            self.mNumParticipants,
            mParticipantInfo,
            self.mUnfilteredThrottle,
            self.mUnfilteredBrake,
            self.mUnfilteredSteering,
            self.mUnfilteredClutch,
            mCarName,
            mCarClassName,
            self.mLapsInEvent,
            mTrackLocation,
            mTrackVariation,
            self.mTrackLength,
            self.mNumSectors,
            self.mLapInvalidated,
            self.mBestLapTime,
            self.mLastLapTime,
            self.mCurrentTime,
            self.mSpeed,
            self.mRpm,
            self.mMaxRPM,
            self.mBrake,
            self.mThrottle,
            self.mClutch,
            self.mSteering,
            self.mGear,
            self.mNumGears,
            self.mOdometerKM,
            self.mAntiLockActive,
            self.mBoostActive,
            self.mBoostAmount,
            ox, oy, oz, # mOrientation
            lvx, lvy, lvz, # mLocalVelocity
            wvx, wvy, wvz, # mWorldVelocity
            avx, avy, avz, # mAngularVelocity
            lax, lay, laz, # mLocalAcceleration
            ttfl, ttfr, ttrl, ttrr, # mTyreTemp
            btfl, btfr, btrl, btrr, # mBrakeTempCelsius
            stfl, stfr, strl, sttrr # mSuspensionTravel

        ) = self.fmt.unpack(buf[:self.fmt.size])

        self.mCarName = mCarName.decode('utf-8').rstrip('\0')
        self.mCarClassName = mCarClassName.decode('utf-8').rstrip('\0')
        self.mTrackLocation = mTrackLocation.decode('utf-8').rstrip('\0')
        self.mTrackVariation = mTrackVariation.decode('utf-8').rstrip('\0')
        self.mLocalAcceleration = Vector(lax, lay, laz)
        self.mTyreTemp = Wheels(ttfl, ttfr, ttrl, ttrr)
        self.mBrakeTempCelsius = Wheels(btfl, btfr, btrl, btrr)
        self.mSuspensionTravel = Wheels(stfl, stfr, strl, sttrr)

        self.participants = []
        #  unpack the participants
        if self.mNumParticipants > 0:

            start = 0
            for _ in range(self.mNumParticipants):
                end = start + AMS2ParticipantInfo.fmt.size
                pdata = mParticipantInfo[start:end]
                participant = AMS2ParticipantInfo(pdata)
                self.participants.append(participant)
                start = end

            self.driver = self.participants[0]
        else:
            self.driver = None









