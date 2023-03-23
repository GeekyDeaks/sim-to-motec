import sqlite3
from stm.motec import MotecLog, MotecEvent, MotecLogExtra
from stm.gt7 import GT7DataPacket
import stm.gps as gps
import os
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description="Convert GT7 sqlite samples to MoTeC log")
parser.add_argument("db", type=str, help="db file to convert")
parser.add_argument("--start", help="start tick")
parser.add_argument("--end", help="end tick")
parser.add_argument("--name", default="test-motec", help="name of the file (used for filename)")
args = parser.parse_args()

out_path = "logs/gt7"

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

event  = MotecEvent({
    "name": args.name,
    "session": "unknown",
    "comment": f"converted by gt7dump-to-motec",
    "venuepos": 0
})

log = MotecLog({
    "date": datetime.today().strftime('%d/%m/%Y'),
    "time": datetime.today().strftime('%H:%M:%S'),
    "driver": "unknown",
    "vehicle": "unknown vehicle",
    "venue": f"unknown",
    "comment": f"converted by gt7dump-to-motec",
    "event": event
})

logx = MotecLogExtra()

for c in channels.keys():

    print(f"""creating channel: {c} / {channels[c]["name"]}""")
    log.add_channel(channels[c])


for record in res.fetchall():

    timestamp, data = record

    p = GT7DataPacket(data)

    if args.start and p.tick < int(args.start):
        continue 

    if args.end and p.tick > int(args.end):
        break

    if p.current_lap < 0:
        continue

    if lastlap is None:
        lastlap = p.current_lap

    if p.current_lap < lastlap:
        print(f"stopping at tick {p.tick} due to session end")
        break # we are done...

    if p.current_lap != lastlap:
        # figure out the laptimes
        if p.last_laptime > 0:
            logx.add_lap(p.last_laptime / 1000.0)
        else:
            # guess it from the number of samples
            logx.add_lap(lap_samples * freq)

        lap_samples = 0
        print(f"adding lap {lastlap}")
    else:
        lap_samples += 1


    lastlap = p.current_lap

    # do some conversions
    # gear, throttle, brake, speed, z, x

    lat, long = gps.convert(x=p.positionX, z=-p.positionZ)

    log.add_samples([
        p.gear & 0x0f,
        p.throttle * 100 / 255,
        p.brake * 100 / 255,
        p.speed * 2.237, # m/s to mph,
        lat,
        long
    ])

    if (p.tick % 100) == 0:
        print(
            f"{timestamp:6} tick: {p.tick:6} {p.positionX:10.5f} {p.positionY:10.5f} {p.positionZ:10.5f}"
            f" {p.speed:3.0f} {p.current_lap:2}/{p.laps:2}"
            f" {p.best_laptime:6}/{p.last_laptime:6}"
            f" {p.race_position:3}/{p.opponents:3} {p.gear & 0x0f} {p.throttle:3} {p.brake:3}"
            f" {p.car_code}"
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
