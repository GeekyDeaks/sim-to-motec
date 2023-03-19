import argparse
from stm.motec import MotecLog
from pprint import pformat
from pathlib import Path

parser = argparse.ArgumentParser(description="MoTeC dump")
parser.add_argument("log", type=str, help="Path to logfile")
parser.add_argument("--outputdir", type=str, default="tmp/dump", help="Output directory")

args = parser.parse_args()

f = open(args.log,'rb')
l = MotecLog.from_string(f.read(), pad=True)

out_dir = Path(args.outputdir)
out_dir = out_dir.joinpath(l.venue)
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir.joinpath("log.txt")

with open(out_file, "w") as fout:
    fout.write(pformat(vars(l), sort_dicts=False))
    fout.write("\n---------------\n")
    fout.write(pformat(vars(l.event), sort_dicts=False))

channel_dir = out_dir.joinpath("channels")
channel_dir.mkdir(parents=True, exist_ok=True)

# dump summary of channels
out_file = out_dir.joinpath(f"channels.txt")
cheaders = ["name", "pos", "next", "data", "samples", "headsize", "datasize" ]
with open(out_file, "w") as fout:
    fout.write("\t".join(cheaders) + "\n")
    for (idx, c) in enumerate(l.channels):
        fout.write("\t".join([
            c.name,
            str(c._start),
            str(c.nextpos),
            str(c.datapos),
            str(c.numsamples),
            str(c.header.size),
            str(c.samples.datasize)
        ]) + "\n")

for (idx, c) in enumerate(l.channels):
    out_file = channel_dir.joinpath(f"{idx:03}_{c.shortname}.txt")
    with open(out_file, "w") as fout:
        fout.write(pformat(vars(c), sort_dicts=False, compact=True))




