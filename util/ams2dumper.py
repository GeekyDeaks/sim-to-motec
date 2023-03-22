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

isodate = datetime.datetime.now().replace(microsecond=0).isoformat().replace('-', '').replace(':', '')
con = sqlite3.connect(os.path.join(PATH, f"ams2-samples-{isodate}.db") )
cur = con.cursor()
cur.execute("CREATE TABLE samples(timestamp int, data blob)")

while True:

    try:

        if wait:
            time.sleep(wait)

        if not shm_b:
            shm_b = shared_memory.SharedMemory("$pcars2$")

        v = fmt.unpack(shm_b.buf[:fmt.size])
        sample_count += 1
        timestamp = int(time.time() * 1000)
        cur.execute("INSERT INTO samples(timestamp, data) VALUES (?, ?)", (timestamp, shm_b.buf))

        if (sample_count % (freq * 10)) == 0:
            print(f"sampled {sample_count} times, last: {v}")
            con.commit()

        wait = 1 / freq

    except FileNotFoundError:
        print("waiting for AMS2 to start")
        wait = 5

    except KeyboardInterrupt:
        print('stopping')
        con.commmit()
        break

con.close()