import argparse
import os
import csv
from stm.motec import MotecLog
import stm.gps as gps
import xml.dom.minidom as minidom
from stm.motec import MotecLog, MotecEvent
from pprint import pprint
from pathlib import Path
from datetime import datetime
import re

parser = argparse.ArgumentParser(description="MoTeC AC raw file converter")
parser.add_argument("inputdir", type=str, help="Path to raw files")
args = parser.parse_args()

dir_list = os.listdir(args.inputdir)

pattern = r"lap[-_](\d+)\.txt"

laps = []

for f in dir_list:
    match = re.match(pattern, f)
    if match:
        laps.append((f, int(match.group(1))))


laps.sort(key=lambda a: a[1])

freq = 1 / 20
samples = []
laptimes = []
mult = [ 1, 100, 100, .1, 1, 1, 1, -1 ]

for (fn, lap) in laps:

    fullname = Path(args.inputdir).joinpath(fn)
    print(f"processing {fullname}")
        
    with open(fullname) as fin:

        reader = csv.reader(fin, delimiter='\t')
        headers = next(reader)[1:]
        next_t = 0
        maxtime = 0

        # start adding the data when it hits a frequency point

        for row in reader:

            timestamp, *values = [ float(v) for v in row ]

            maxtime = timestamp

            if timestamp < next_t:
                continue

            next_t += freq
            mv = [ (v * mult[i]) for (i, v) in enumerate(values)]

            # convert x and z to lat / long
            mv[7], mv[5] = gps.convert(x=mv[5], z=mv[7], latmid=54.45542226228547, longmid=-1.5547022498076541)
            samples.append(mv)

        laptimes.append(maxtime)

print(f"found columns: {headers}")
print(f"got {len(samples)} samples")

# dump the samples
with open(Path(args.inputdir).joinpath("_samples.txt"), "w") as fout:
    for s in samples:
        fout.write("\t".join([ str(v) for v in s ]) + "\n")

# dump the laptime
with open(Path(args.inputdir).joinpath("_laptimes.txt"), "w") as fout:
    for (idx, l) in enumerate(laptimes):
        fout.write(f"{idx}\t{l}\n")

# assume first lap is outlap and lastlap is inlap

def create_xml(laps):

    # build up the beacon markers
    markers = []
    elapsedtime = 0

    # ignore the last lap
    laps = laps[:-1]

    for (idx, laptime) in enumerate(laps):

        elapsedtime += laptime * 1000000 # micro seconds
        marker = idx + 1
        m = f"""        <Marker Version="100" ClassName="BCN" Name="Manual.{marker}" Flags="77" Time="{elapsedtime}"/>"""
        markers.append(m)

    beacons = len(markers) - 1

    totallaps = len(markers) + 1 # count the in lap

    laps_without_outlap = laps[1:]

    fastestlap, fastesttime = sorted(enumerate(laps_without_outlap), key=lambda a: float(a[1]))[0]

    fastestlap += 2
    minutes = int(fastesttime % 3600 // 60)
    seconds = fastesttime % 3600 % 60

    fastesttime = f"{minutes:02d}:{seconds:06.3f}"

    xmllines = [
        """<?xml version="1.0"?>""",
        """<LDXFile Locale="English_United Kingdom.1252" DefaultLocale="C" Version="1.6">"""
        """<Layers>""",
        """  <Layer>""",
        """    <MarkerBlock>""",
       f"""      <MarkerGroup Name="Beacons" Index="{beacons}">""",
        *markers,
        """      </MarkerGroup>""",
        """    </MarkerBlock>""",
        """    <RangeBlock/>""",
        """  </Layer>""",
        """  <Details>""",
       f"""    <String Id="Total Laps" Value="{totallaps}"/>""",
       f"""    <String Id="Fastest Time" Value="{fastesttime}"/>""",
       f"""    <String Id="Fastest Lap" Value="{fastestlap}"/>""",
        """  </Details>""",
        """</Layers>""",
        """</LDXFile>"""
    ]
    return("\n".join(xmllines))


# dump the ldx
with open(Path(args.inputdir).joinpath("motec.ldx"), "w") as fout:
    fout.write(create_xml(laptimes))



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
    "gas": {
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
    "speed_Mph": {
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
    "steer": {
        "id": 50018,
        "datatype": 3,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "Steered Angle",
        "shortname": "Str Ang",
        "units": "deg"
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
        "name": "GPS Latitude", # GPS Latitude
        "shortname": "GPSLat",  # GPSLat
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

name = args.inputdir.replace("/", "_").replace(".", "")
					
event  = MotecEvent({
    "name": f"event_{name}",
    "session": "unknown session",
    "comment": f"converted from {args.inputdir}",
    "venuepos": 0
})

log = MotecLog({
    "date": datetime.today().strftime('%d/%m/%Y'),
    "time": datetime.today().strftime('%H:%M:%S'),
    "driver": "unknown driver",
    "vehicle": "unknown vehicle",
    "venue": f"{name}",
    "comment": f"converted from {args.inputdir}",
    "event": event
})

cols = []
# create the channels
for (idx, header) in enumerate(headers):

    if header not in channels:
        continue

    print(f"using column: {header}")
    cols.append(idx)
    log.add_channel(channels[header])

# now read in the data
for row in samples:
    log.add_samples([ row[c] for c in cols])

with open(Path(args.inputdir).joinpath("motec.ld"), "wb") as fout:
    fout.write(log.to_string())

with open(Path(args.inputdir).joinpath("motec.ld"), "rb") as f:
    l = MotecLog.from_string(f.read())
    pprint(vars(l))


