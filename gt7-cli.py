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

    parser = argparse.ArgumentParser(description="Log GT7 samples to MoTeC i2")
    parser.add_argument("addr", type=str, help="ip address of playstation or raw file")
    parser.add_argument("--driver", type=str, default="", help="Driver name")
    parser.add_argument("--session", type=str, default="", help="Session e.g. Practice, Qualify, Race")
    parser.add_argument("--vehicle", type=str, default="", help="Override name of vehicle")
    parser.add_argument("--venue", type=str, default="", help="Venue/Track name, MoTeC will not generate a track map without this")
    parser.add_argument("--replay", action="store_true", help="log replay telemetry")
    parser.add_argument("--imperial", action="store_true", help="use imperial units")
    parser.add_argument("--freq", type=int, default=60, help="frequency to collect samples, currently ignored")
    parser.add_argument("--saveraw", help="save raw samples to an sqlite3 db for later analysis", action="store_true")
    parser.add_argument("--loadraw", help="load raw samples from an sqlite3 db", action="store_true")
    args = parser.parse_args()

    filetemplate = os.path.join("logs", "gt7", "{venue}_{vehicle}_{driver}_{session}_{datetime}")

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
        replay=args.replay,
        driver=args.driver,
        session=args.session,
        vehicle=args.vehicle,
        venue=args.venue,
        imperial=args.imperial
    )

    try:
        logger.start()
        while logger.is_alive():
            logger.join(0.1)
    except KeyboardInterrupt:
        l.warning("stopping")
        logger.stop()
        logger.join()

if __name__ == '__main__':
    main()
