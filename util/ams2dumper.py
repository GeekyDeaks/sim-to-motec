# crude script to sample the shared memory from AMS2 to an sqlite DB for later analysis
# files get written to logs/raw/ams2-samples-[TIMESTAMP].db
import struct
import time
import datetime
import sqlite3
import os
from multiprocessing import shared_memory

PATH = "logs/raw"
os.makedirs(PATH, exist_ok=True)

shm_b = None

# simple snapshot structure to allow a bit of logic in the sampling
fmt = struct.Struct(
    "<"
    "I" # mVersion
    "I" # mBuildVersionNumber
    "I" # mGameState
    "I" # mSessionState
    "I" # mRaceState
)

freq = 20
wait = 0
sample_count = 0
saved_count = 0
next_sample = 0

isodate = datetime.datetime.now().replace(microsecond=0).isoformat().replace('-', '').replace(':', '')
con = sqlite3.connect(os.path.join(PATH, f"ams2-samples-{isodate}.db") )
cur = con.cursor()
cur.execute("CREATE TABLE samples(timestamp int, data blob)")

while True:

    try:

        if wait:
            time.sleep(wait)

        now = time.time() # when

        if not shm_b:
            shm_b = shared_memory.SharedMemory("$pcars2$")
            print("connected to AMS2 shared memory")
            next_sample = now

        v = fmt.unpack(shm_b.buf[:fmt.size])
        sample_count += 1

        if v[2] == 2: # mGameState = PLAYING
            saved_count += 1
            
            cur.execute("INSERT INTO samples(timestamp, data) VALUES (?, ?)", (int(now * 1000), shm_b.buf))

        if (sample_count % (freq * 10)) == 0:
            print(f"saved {saved_count} samples out of {sample_count}, last: {v}")
            con.commit()

        # work out when the next sample will be
        now = time.time()
        next_sample = max(next_sample + (1 / freq), now)
        wait = next_sample - now

    except FileNotFoundError:
        print("waiting for AMS2 to start")
        wait = 5

    except KeyboardInterrupt:
        print('stopping')
        con.commit()
        break

con.close()