from struct import Struct

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
            self.mWorldPositionX,
            self.mWorldPositionY,
            self.mWorldPositionZ,
            self.mCurrentLapDistance,
            self.mRacePosition,
            self.mLapsCompleted,
            self.mCurrentLap,
            self.mCurrentSector

        ) = self.fmt.unpack(buf[:self.fmt.size])

        self.mName = mName.decode('latin-1').rstrip('\0')

    @property
    def size(self):
        return self.fmt.size


class AMS2SharedMemory:

    fmt = Struct(
        "<"
        "I" # mVersion
        "I" # mBuildVersionNumber
        "I" # mGameState
        "I" # mSessionState
        "I" # mRaceState
        "i" # mViewedParticipantIndex
        "i" # mNumParticipants
        # STORED_PARTICIPANTS_MAX * AMS2ParticipantInfo.size
        "6400s" # mParticipantInfo
        "f" # mUnfilteredThrottle
        "f" # mUnfilteredBrake
        "f" # mUnfilteredSteering
        "f" # mUnfilteredClutch
        "64s" # mCarName
        "64s" # mCarClassName
        "I" # mLapsInEvent
        "64s" # mTrackLocation
        "64s" # mTrackVariation
        "f" # mTrackLength
        "i" # mNumSectors
        "?" # mLapInvalidated
        "3x" # alignment padding
        "f" # mBestLapTime
        "f" # mLastLapTime



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
            self.mLastLapTime
        ) = self.fmt.unpack(buf[:self.fmt.size])

        self.mCarName = mCarName.decode('utf-8').rstrip('\0')
        self.mCarClassName = mCarClassName.decode('utf-8').rstrip('\0')
        self.mTrackLocation = mTrackLocation.decode('utf-8').rstrip('\0')
        self.mTrackVariation = mTrackVariation.decode('utf-8').rstrip('\0')

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









