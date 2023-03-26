CHANNELS = {
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
    "lat": {
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
    "long": {
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

def get_channel_definition(name, freq=20):

    if name not in CHANNELS:
        return
    cd = dict(CHANNELS[name])
    cd["freq"] = freq

