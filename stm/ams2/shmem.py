from struct import Struct

class AMS2ParticipantInfo:

    fmt = Struct(
        "<"
        "?" # mIsActive
        "63s" # mName (STRING_LENGTH_MAX - 1)
        "3f" #  mWorldPosition
        "d" # mCurrentLapDistance
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

        self.mName = mName.decode('utf-8').rstrip('\0')

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
            mParticipantInfo

        ) = self.fmt.unpack(buf[:self.fmt.size])

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









