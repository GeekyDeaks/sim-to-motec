# determine drift in sampling
import sqlite3
import argparse

parser = argparse.ArgumentParser(description="Raw sample drift analysis")
parser.add_argument("db", type=str, help="db file to analyse")
parser.add_argument("--freq", type=int)
args = parser.parse_args()


con = sqlite3.connect(args.db)
cur = con.cursor()
if not args.freq:
    try:
        res = cur.execute("SELECT value FROM settings WHERE name='freq'")
        (freq, ) = res.fetchone()
    except:
        freq = args.freq
else:
    freq = args.freq

res = cur.execute("SELECT timestamp, data FROM samples ORDER BY timestamp")

lastts = None
firstts = None
scount = 0
lastfreqts = None

freqcount = 0
sumts = 0
sumfreqts = 0

sumdeltats = 0
duplicates = 0

for (ts, data) in res:

    scount += 1
    sumts += ts

    if data is None:
        duplicates += 1

    if lastts is None:
        lastts = ts
        firstts = ts
        continue

    sumdeltats += ts - lastts

    if (scount % freq) == 0:
        if lastfreqts is not None:
            freqcount += 1
            sumfreqts += ts - lastfreqts
        lastfreqts = ts

    lastts = ts


expected_duration = (scount - 1) * (1 / freq)
actual_duration = lastts - firstts
drift = actual_duration - expected_duration

print(f"freq:                 {freq:11.0f} Hz")
print(f"samples:              {scount:11.0f}")
print(f"duplicates:           {duplicates:11.0f}")
print(f"avg delta:            {sumdeltats/(scount - 1):11.3f} ms")
print(f"avg per second delta: {sumfreqts/freqcount:11.3f} ms")
print(f"expected duration:    {expected_duration:11.3f} ms")
print(f"actual duration:      {actual_duration:11.3f} ms")
print(f"total drift:          {drift:11.3f} ms")