import argparse
import sqlite3
from stm.ams2 import AMS2SharedMemory

parser = argparse.ArgumentParser(description="Analyse AMS2 raw samples")
parser.add_argument("db", type=str, help="db file to check")
parser.add_argument("name", default="mParticipant", help="name of the variable")
args = parser.parse_args()


con = sqlite3.connect( args.db )
cur = con.cursor()
res = cur.execute("select * from samples")

vtype = None
vmin = None
vmax = None
vsum = 0
samples = 0
vstr = {}

def getvar(p, name):

    # split the name
    names = name.split(".")
    v = p
    for n in names:
        v = getattr(v, n)

    return v




for timestamp, data in res:

    if not data:
        continue

    p = AMS2SharedMemory(data)


    try:

        samples += 1

        v = getvar(p, args.name)

        vtype = type(v)
        if isinstance(v, int) or isinstance(v, float):
            # get the min and max
            if vmax is None or vmax < v:
                vmax = v

            if vmin is None or vmin > v:
                vmin = v

            vsum += v

        if isinstance(v, str):
            if v not in vstr:
                vstr[v] = 0

            vstr[v] += 1

    except:
        pass

print(f"type: {vtype}")

if vsum:
    print(f"vmin: {vmin}")
    print(f"vmax: {vmax}")
    print(f"vavg: {vsum/samples}")


print(f"vstr: {vstr}")