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
from stm.ams2 import AMS2Sampler, AMS2Logger

def main():

    parser = argparse.ArgumentParser(description="Log AMS2 samples to MoTeC i2")
    parser.add_argument("--freq", type=int, default=20, help="frequency (Hz) to collect samples")
    parser.add_argument("--saveraw", help="save raw samples to an sqlite3 db for later analysis", action="store_true")
    parser.add_argument("--loadraw", help="load raw samples from an sqlite3 db", default="")

    args = parser.parse_args()

    filetemplate = os.path.join("logs", "ams2", "{name}_{driver}_{venue}_{vehicle}_{datetime}_{session}")

    if args.saveraw:
        rawfile = os.path.join("logs", "raw", "ams2", f"{time.time():.0f}.db" )
    else:
        rawfile = None

    if args.loadraw:
        sampler = RawSampler(rawfile=args.loadraw)
    else:
        sampler = AMS2Sampler(freq=args.freq)

    logger = AMS2Logger(
        rawfile=rawfile,
        sampler=sampler,
        filetemplate=filetemplate
    )

    try:
        logger.start()
        logger.join()
    except KeyboardInterrupt:
        l.warning("stopping")
        logger.stop()
        logger.join()

if __name__ == '__main__':
    main()
