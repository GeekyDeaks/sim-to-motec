
#include <stdio.h>
#include <stdbool.h>
#include <stddef.h>
#include "SharedMemory.h"

// gcc stm/ams2/shm_info.c -o shm_info

int main()
{
    printf("sizeof(ParticipantInfo) == %lu\n", sizeof(ParticipantInfo));
    printf("sizeof(SharedMemory) == %lu\n", sizeof(SharedMemory));
    printf("sizeof(float) = %lu\n", sizeof(float));
    printf("offsetof(mSequenceNumber) = %lu\n", offsetof(SharedMemory, mSequenceNumber));
    printf("offsetof(mClutchTemp) = %lu\n", offsetof(SharedMemory, mClutchTemp));
    printf("offsetof(mRaceState) = %lu\n", offsetof(SharedMemory, mRaceState));
}