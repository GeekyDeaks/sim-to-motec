from struct import Struct
from enum import Enum
from collections import namedtuple
from stm.maths import Vector

Wheels = namedtuple("Wheels", ["fl", "fr", "rl", "rr"])
Wings = namedtuple("Wing", ["front", "rear"])

def decode_string(s):
    if s:
        return s.decode('utf-8').split('\0')[0]

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

class AMS2CarFlags(Enum):
    CAR_HEADLIGHT         = (1<<0)
    CAR_ENGINE_ACTIVE     = (1<<1)
    CAR_ENGINE_WARNING    = (1<<2)
    CAR_SPEED_LIMITER     = (1<<3)
    CAR_ABS               = (1<<4)
    CAR_HANDBRAKE         = (1<<5)
    CAR_TCS               = (1<<6)
    CAR_SCS               = (1<<7)

class AMS2DrsState(Enum):
	DRS_INSTALLED       = (1<<0) # Vehicle has DRS capability
	DRS_ZONE_RULES      = (1<<1) # 1 if DRS uses F1 style rules
	DRS_AVAILABLE_NEXT  = (1<<2) # detection zone was triggered (only applies to f1 style rules)
	DRS_AVAILABLE_NOW   = (1<<3) # detection zone was triggered and we are now in the zone (only applies to f1 style rules)
	DRS_ACTIVE          = (1<<4) # Wing is in activated state

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
        self.mName = decode_string(mName)

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
        "f"     # mSplitTimeAhead
        "f"     # mSplitTimeBehind
        "f"     # mSplitTime
        "76x"   # skip a load of stuff we are not currently interested in
        "I"     # mCarFlags
        "f"     # mOilTempCelsius
        "f"     # mOilPressureKPa
        "f"     # mWaterTempCelsius
        "f"     # mWaterPressureKPa
        "f"     # mFuelPressureKPa
        "f"     # mFuelLevel
        "f"     # mFuelCapacity
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
        "3f"    # mWorldAcceleration
        "12x"   # mExtentsCentre
        "16x"   # mTyreFlags
        "16x"   # mTerrain
        "4f"    # mTyreY
        "4f"    # mTyreRPS
        "4f"    # mTyreSlipSpeed
        "4f"    # mTyreTemp
        "4f"    # mTyreGrip
        "4f"    # mTyreHeightAboveGround
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
        "f"     # mAmbientTemperature
        "f"     # mTrackTemperature
        "4x"    # mRainDensity 
        "4x"    # mWindSpeed
        "4x"    # mWindDirectionX
        "4x"    # mWindDirectionY
        "4x"    # mCloudBrightness
        "i"     # mSequenceNumber
        "16x"   # mWheelLocalPositionY      
        "4f"    # mSuspensionTravel
        "4f"    # mSuspensionVelocity
        "4f"    # mAirPressure
        "4x"    # mEngineSpeed
        "f"     # mEngineTorque
        "2f"    # mWings
        "4x"    # mHandBrake
        "256x"  # mCurrentSector1Times
        "256x"  # mCurrentSector2Times
        "256x"  # mCurrentSector3Times
        "256x"  # mFastestSector1Times
        "256x"  # mFastestSector2Times
        "256x"  # mFastestSector3Times
        "256x"  # mFastestLapTimes
        "256x"  # mLastLapTimes
        "64x"   # mLapsInvalidated
        "256x"  # mRaceStates
        "256x"  # mPitModes
        "768x"  # mOrientations
        "256x"  # mSpeeds
        "4096x" # mCarNames
        "4096x" # mCarClassNames
        "4x"    # mEnforcedPitStopLap
        "64s"   # mTranslatedTrackLocation
        "64s"   # mTranslatedTrackVariation
        "f"     # mBrakeBias
        "f"     # mTurboBoostPressure
        "160x"  # mTyreCompound
        "256x"  # mPitSchedules
        "256x"  # mHighestFlagColours
        "256x"  # mHighestFlagReasons
        "256x"  # mNationalities
        "4x"    # mSnowDensity
        "4x"    # mSessionDuration
        "4x"    # mSessionAdditionalLaps
        "4f"    # mTyreTempLeft
        "4f"    # mTyreTempCenter
        "4f"    # mTyreTempRight
        "I"     # mDrsState,
        "4f"    # mRideHeight
        "I"     # mJoyPad0
        "I"     # mDPad
        "i"     # mAntiLockSetting
        "i"     # mTractionControlSetting
        "i"     # mErsDeploymentMode
        "?"     # mErsAutoModeEnabled
        "3x"    # alignment padding
        "f"     # mClutchTemp
        "f"     # mClutchWear
        "f"     # mClutchOverheated
        "f"     # mClutchSlipping
        "i"     # mYellowFlagState
        "?"     # mSessionIsPrivate
        "3x"    # alignment padding
        "I"     # mLaunchStage
    )

    def __init__(self, buf):

        (
            self.mVersion, 
            self.mBuildVersionNumber,
            mGameState,
            mSessionState,
            mRaceState,
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
            self.mSplitTimeAhead,
            self.mSplitTimeBehind,
            self.mSplitTime,
            self.mCarFlags,
            self.mOilTempCelsius,
            self.mOilPressureKPa,
            self.mWaterTempCelsius,
            self.mWaterPressureKPa,
            self.mFuelPressureKPa,
            self.mFuelLevel,
            self.mFuelCapacity,
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
            wax, way, waz, # mWorldAcceleration
            tyfl, tyfr, tyrl, tyrr, # mTyreY
            trpsfl, trpsfr, trpsrl, trpsrr, # mTyreRPS
            tssfl, tssfr, tssrl, tssrr, # mTyreSlipSpeed
            ttfl, ttfr, ttrl, ttrr, # mTyreTemp
            tgfl, tgfr, tgrl, tgrr, # mTyreGrip
            thagfl, thagfr, thagrl, thagrr, # mTyreHeightAboveGround
            btfl, btfr, btrl, btrr, # mBrakeTempCelsius
            self.mAmbientTemperature,
            self.mTrackTemperature,
            self.mSequenceNumber,
            stfl, stfr, strl, sttrr, # mSuspensionTravel
            svfl, svfr, svrl, svrr, # mSuspensionVelocity
            apfl, apfr, aprl, aprr, # mAirPressure,
            self.mEngineTorque,
            wf, wr, # mWings
            mTranslatedTrackLocation,
            mTranslatedTrackVariation,
            self.mBrakeBias,
            self.mTurboBoostPressure,
            ttlfl, ttlfr, ttlrl, ttlrr,
            ttcfl, ttcfr, ttcrl, ttcrr,
            ttrfl, ttrfr, ttrrl, ttrrr,
            self.mDrsState,
            rhfl, rhfr, rhrl, rhrr, # mRideHeight
            self.mJoyPad0,
            self.mDPad,
            self.mAntiLockSetting,
            self.mTractionControlSetting,
            self.mErsDeploymentMode,
            self.mErsAutoModeEnabled,
            self.mClutchTemp,
            self.mClutchWear,
            self.mClutchOverheated,
            self.mClutchSlipping,
            self.mYellowFlagState,
            self.mSessionIsPrivate,
            self.mLaunchStage

        ) = self.fmt.unpack(buf[:self.fmt.size])

        self.mGameState = AMS2GameState(mGameState)
        self.mSessionState = AMS2SessionState(mSessionState)
        self.mRaceState = AMS2RaceState(mRaceState)
        self.mCarName = decode_string(mCarName)
        self.mCarClassName = decode_string(mCarClassName)
        self.mTrackLocation = decode_string(mTrackLocation)
        self.mTrackVariation = decode_string(mTrackVariation)
        self.mTranslatedTrackLocation = decode_string(mTranslatedTrackLocation)
        self.mTranslatedTrackVariation = decode_string(mTranslatedTrackVariation)
        self.mOrientation = Vector(ox, oy, oz)
        self.mLocalVelocity = Vector(lvx, lvy, lvz)
        self.mWorldVelocity = Vector(wvx, wvy, wvz)
        self.mAngularVelocity = Vector(avx, avy, avz)
        self.mLocalAcceleration = Vector(lax, lay, laz)
        self.mWorldAcceleration = Vector(wax, way, waz)
        self.mTyreY = Wheels(tyfl, tyfr, tyrl, tyrr)
        self.mTyreRPS = Wheels(trpsfl, trpsfr, trpsrl, trpsrr)
        self.mTyreSlipSpeed = Wheels(tssfl, tssfr, tssrl, tssrr)
        self.mTyreTemp = Wheels(ttfl, ttfr, ttrl, ttrr)
        self.mTyreGrip = Wheels(tgfl, tgfr, tgrl, tgrr)
        self.mTyreHeightAboveGround = Wheels(thagfl, thagfr, thagrl, thagrr)
        self.mBrakeTempCelsius = Wheels(btfl, btfr, btrl, btrr)
        self.mSuspensionTravel = Wheels(stfl, stfr, strl, sttrr)
        self.mSuspensionVelocity = Wheels(svfl, svfr, svrl, svrr)
        self.mAirPressure = Wheels(apfl, apfr, aprl, aprr)
        self.mWings = Wings(wf, wr)
        self.mTyreTempLeft = Wheels(ttlfl, ttlfr, ttlrl, ttlrr)
        self.mTyreTempCenter = Wheels(ttcfl, ttcfr, ttcrl, ttcrr)
        self.mTyreTempRight = Wheels(ttrfl, ttrfr, ttrrl, ttrrr)
        self.mRideHeight = Wheels(rhfl, rhfr, rhrl, rhrr)

        self.tcsActive = bool(self.mCarFlags & AMS2CarFlags.CAR_TCS.value)
        self.scsActive = bool(self.mCarFlags & AMS2CarFlags.CAR_SCS.value)
        self.absActive = bool(self.mCarFlags & AMS2CarFlags.CAR_ABS.value)

        self.drsAvailable = bool(self.mDrsState & AMS2DrsState.DRS_AVAILABLE_NOW.value)
        self.drsActive = bool(self.mDrsState & AMS2DrsState.DRS_ACTIVE.value)

        self.participants = []
        driver_index = self.mViewedParticipantIndex
        #  unpack the participants
        if self.mNumParticipants > 0 and driver_index >= 0:

            start = 0
            for _ in range(self.mNumParticipants):
                end = start + AMS2ParticipantInfo.fmt.size
                pdata = mParticipantInfo[start:end]
                participant = AMS2ParticipantInfo(pdata)
                self.participants.append(participant)
                start = end

            self.driver = self.participants[driver_index]
        else:
            self.driver = None









