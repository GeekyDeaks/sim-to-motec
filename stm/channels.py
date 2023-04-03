CHANNELS = {
    "gear": {
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
    "lat": {
        "datatype": 5,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 7,
        "name": "GPS Latitude",
        "shortname": "GPSLat",
        "units": "deg"
    },
    "long": {
        "datatype": 5,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 7,
        "name": "GPS Longitude",
        "shortname": "GPSLong",
        "units": "deg"
    },
    "beacon": {
        "datatype": 0,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "Beacon",
        "shortname": "Beacon",
        "units": ""
    },
    "lap": {
        "datatype": 3,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "Lap Number",
        "shortname": "Lap",
        "units": ""
    },
    "rpm": {
        "datatype": 3,
        "datasize": 2,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 0,
        "name": "Engine RPM",
        "shortname": "RPM",
        "units": "rpm"
    },
    "velx": {
        "datatype": 5,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 3,
        "name": "Velocity X",
        "shortname": "VELX",
        "units": "m"
    },
    "vely": {
        "datatype": 5,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 3,
        "name": "Velocity Y",
        "shortname": "VELY",
        "units": "m"
    },
    "velz": {
        "datatype": 5,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 3,
        "name": "Velocity Z",
        "shortname": "VELZ",
        "units": "m"
    },
    "glat": {
        "datatype": 5,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 2,
        "name": "G Force Lat",
        "shortname": "G Lat",
        "units": "G"
    },
    "gvert": {
        "datatype": 5,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 2,
        "name": "G Force Vert",
        "shortname": "G Vert",
        "units": "G"
    },
    "glong": {
        "datatype": 5,
        "datasize": 4,
        "freq": 20,
        "shift": 0,
        "multiplier": 1,
        "scale": 1,
        "decplaces": 2,
        "name": "G Force Long",
        "shortname": "G Long",
        "units": "G"
    }
}

START_ID = 8000

for (i, v) in enumerate(CHANNELS.values()):
    if "id" not in v:
        v["id"] = START_ID + i

def get_channel_definition(name, freq=None):

    if freq is None:
        freq = 20

    cd = dict(CHANNELS[name])
    cd["freq"] = freq
    return cd