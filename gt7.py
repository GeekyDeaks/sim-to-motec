from logging import getLogger, basicConfig, DEBUG
basicConfig(
     level=DEBUG,
     format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
     datefmt="%Y-%m-%d %H:%M:%S"
)
l = getLogger(__name__)

import argparse
import os
import time
from stm.sampler import RawSampler
from stm.gt7 import GT7Logger, GT7Sampler

def main():

    parser = argparse.ArgumentParser(description="Log GT7 samples to MoTeC")
    parser.add_argument("addr", type=str, help="ip address of playstation or raw file")
    parser.add_argument("--name", default="test-motec", help="name of the file (used for filename prefix)")
    parser.add_argument("--driver", type=str, default="", help="Driver name")
    parser.add_argument("--session", type=str, default="", help="Session e.g. Practice, Qualify, Race")
    parser.add_argument("--vehicle", type=str, default="", help="Override name of vehicle")
    parser.add_argument("--venue", type=str, default="", help="Venue/Track name, MoTeC will not generate a track map without this")
    parser.add_argument("--freq", type=int, default=60, help="frequency to collect samples, currently ignored")
    parser.add_argument("--saveraw", help="save raw samples to an sqlite3 db for later analysis", action="store_true")
    parser.add_argument("--loadraw", help="load raw samples from an sqlite3 db", action="store_true")
    args = parser.parse_args()

    filetemplate = os.path.join("logs", "gt7", "{name}_{driver}_{venue}_{session}_{vehicle}_{datetime}")

    if args.saveraw:
        rawfile = os.path.join("logs", "raw", "gt7", f"{time.time():.0f}.db" )
    else:
        rawfile = None

    if args.loadraw:
        sampler = RawSampler(rawfile=args.addr)
    else:
        sampler = GT7Sampler(addr=args.addr, freq=args.freq)

    logger = GT7Logger(
        rawfile=rawfile,
        sampler=sampler,
        filetemplate=filetemplate,
        name=args.name, 
        driver=args.driver,
        session=args.session,
        vehicle=args.vehicle,
        venue=args.venue
    )

    logger.start()

if __name__ == '__main__':
    main()
