import sqlite3
from stm.motec import MotecLog, MotecEvent, MotecLogExtra
from stm.ams2 import AMS2SharedMemory
import stm.gps as gps
import os
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description="Convert AMS2 sqlite samples to MoTeC log")
parser.add_argument("db", type=str, help="db file to convert")
parser.add_argument("--name", default="test-motec", help="name of the file (used for filename)")
args = parser.parse_args()

out_path = "logs/ams2"

channels = {
    "gear": {
        "id": 50078,
        "datatype": 3,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "Gear",
        "shortname": "Gear",
        "units": ""
    },
    "throttle": {
        "id": 50014,
        "datatype": 3,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "Throttle Pos",
        "shortname": "Thr Pos",
        "units": "%"
    },
    "brake": {
        #"id": 50015,
        "id": 10001,
        "datatype": 3,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "Brake Pos",
        "shortname": "Brk Pos",
        "units": "%"
    },
    "steer": {
        "id": 50018,
        "datatype": 3,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 2,
        "name": "Steered Angle",
        "shortname": "Str Ang",
        "units": "deg"
    },
    "speed": {
        #"id": 50000,
        "id": 10000,
        "datatype": 3,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "Ground Speed",
        "shortname": "Gnd Spd",
        "units": "mph"
    },
    "z": {
        "id": 10002,
        "datatype": 7,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "GPS Latitude",
        "shortname": "GPSLat",
        "units": "deg"
    },
    "x": {
        "id": 10003,
        "datatype": 7,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "GPS Longitude",
        "shortname": "GPSLong",
        "units": "deg"
    }

}

con = sqlite3.connect( args.db )
cur = con.cursor()
res = cur.execute("select * from samples")

lastlap = None
freq = 1 / 20
lap_samples = 0
started = False


log = None

for (scount, record) in enumerate(res.fetchall()):

    timestamp, data = record

    p = AMS2SharedMemory(data)

    # get the first participant (us)
    if not len(p.participants):
        continue

    driver = p.participants[0]

    if not log:
        # create the log files
        now = datetime.now().isoformat()

        event  = MotecEvent({
            "name": args.name,
            "session": "unknown",
            "comment": f"converted by ams2dump-to-motec at {now}",
            "venuepos": 0
        })

        log = MotecLog({
            "date": datetime.fromtimestamp(timestamp / 1000).strftime('%d/%m/%Y'),
            "time": datetime.fromtimestamp(timestamp / 1000).strftime('%H:%M:%S'),
            "driver": driver.mName,
            "vehicle": p.mCarName,
            "venue": p.mTrackLocation,
            "comment": f"converted by ams2dump-to-motec at {now}",
            "event": event
        })

        logx = MotecLogExtra()

        for c in channels.keys():

            print(f"""creating channel: {c} / {channels[c]["name"]}""")
            log.add_channel(channels[c])

    if not started and driver.mCurrentLap == 1 and p.mLapInvalidated:
        # AMS2 reports the run up to the start line as an invalid lap1
        driver.mCurrentLap = 0
    else:
        started = True

    if lastlap is None:
        lastlap = driver.mCurrentLap

    if driver.mCurrentLap != lastlap:
        # figure out the laptimes
        if p.mLastLapTime > 0:
            logx.add_lap(p.mLastLapTime)
        else:
            # guess it from the number of samples
            logx.add_lap(lap_samples * freq)

        lap_samples = 0
        print(f"adding lap {lastlap}")
    else:
        lap_samples += 1

    lastlap = driver.mCurrentLap


    # do some conversions

    # gear, throttle, brake, speed, z, x
    lat, long = gps.convert(x=-driver.mWorldPositionX, z=-driver.mWorldPositionZ)

    log.add_samples([
        p.mGear,
        p.mThrottle * 100,
        p.mBrake * 100,
        p.mSteering,
        p.mSpeed, # m/s to mph,
        lat,
        long
    ])

    if (scount % 100) == 0:
        print(
            f"{timestamp:6} {driver.mWorldPositionX:11.5f} {driver.mWorldPositionY:11.5f} {driver.mWorldPositionZ:11.5f}"
            f" {driver.mCurrentLap:2} {driver.mCurrentSector:2} {p.mLapInvalidated}"
            f" {p.mBestLapTime:6.2f}/{p.mLastLapTime:6.2f}"
            f" {p.mUnfilteredThrottle:4.2f} {p.mUnfilteredBrake:4.2f} {p.mUnfilteredSteering:5.2f}"
        )

con.close()

os.makedirs(out_path, exist_ok=True)

# dump the ldx
ldxfilename = os.path.join(out_path, f"{args.name}.ldx")
print(f"writing laptimes to {ldxfilename}")
with open(ldxfilename, "w") as fout:
    fout.write(logx.to_string())

# dump the log
ldfilename = os.path.join(out_path, f"{args.name}.ld")
print(f"writing MoTeC log to {ldfilename}")
with open(ldfilename, "wb") as fout:
    fout.write(log.to_string())