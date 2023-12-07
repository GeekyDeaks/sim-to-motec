import os
import json
import math
import stm.gps as gps
from logging import getLogger
l = getLogger(__name__)

PATH=os.path.dirname(__file__)

TRACKS = {}

class AMS2Track:

    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])


    def convert_to_gps(self, x, z):

        # tweak the x, z as required
        # courtesy of viper4r from https://github.com/eckhchri/pcars-ds-liveview/blob/master/calc_coordinates.js

        x *= self.cor_PosX_mul
        z *= self.cor_PosY_mul

        if self.rotation != 0:
            rotation = math.radians(self.rotation)
            rx = (math.cos(rotation) * x) - (math.sin(rotation) * z)
            rz = (math.sin(rotation) * x) + (math.cos(rotation) * z)

            x = rx
            z = rz 
            
        return gps.convert(x=x, z=z, latmid=self.refLat, longmid=self.refLong)

def lookup_track(name):
    return TRACKS.get(name)

def convert_to_gps(name, x, z):
    track = lookup_track(name)
    if track:
        return track.convert_to_gps(x, z)
    else:
        return gps.convert(x, z)

with open(os.path.join(PATH, "tracks", "gps.json"), "r") as fin:
    track_list = json.loads(fin.read())

    # loop around each track
    for track_data in track_list:

        name = track_data["trackVariation"]

        TRACKS[name] = AMS2Track(track_data)






