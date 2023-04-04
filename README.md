# sim-to-motec

Simple racing/driving sim telemetry to MoTeC log conversion

Currently supports AMS2 and GT7

# Getting started

    git clone https://github.com/GeekyDeaks/sim-to-motec.git
    cd sim-to-motec
    python3 -m venv py
    source py/bin/activate
    pip install -r requirements.txt

# GT7

Convert UDP packets from the GT7 telemetry to a MoTeC i2 log file.  Currently can determine the car, but not the venue/track 
which is required for MoTeC to generate a track map from the fake GPS. Expects UDP samples to arrive at 60Hz and will pad
missing samples, so unlikely to work correctly with 120Hz or VRR without changes to the sampling or logging logic.

A new i2 log file will be created each time the logic detects a session change, usually via the lap number decreasing.

Example:

    python gt7.py 192.168.1.101 --driver "Wilma Cargo" --venue "Brands Hatch"

Usage:

    python gt7.py [-h] [--name NAME] [--driver DRIVER] [--session SESSION] [--vehicle VEHICLE] [--venue VENUE] [--freq FREQ] [--saveraw] [--loadraw] addr

    positional arguments:
        addr               ip address of playstation or raw file

    options:
        -h, --help         show this help message and exit
        --name NAME        name of the file (used for filename prefix)
        --driver DRIVER    Driver name
        --session SESSION  Session e.g. Practice, Qualify, Race
        --vehicle VEHICLE  Override name of vehicle
        --venue VENUE      Venue/Track name, MoTeC will not generate a track map without this
        --freq FREQ        frequency to collect samples, currently ignored
        --saveraw          save raw samples to an sqlite3 db for later analysis
        --loadraw          load raw samples from an sqlite3 db


The CSV file containing the car IDs used to determine the vehicle name can be updated via the following command:

    curl https://raw.githubusercontent.com/ddm999/gt7info/web-new/_data/db/cars.csv -o stm/gt7/cars.csv

# AMS2

Convert AMS2 samples from shared memory to MoTeC i2 log files.  Currently can detect the car and venue as well as the session type.

Example:

    python ams2.py

Usage:

    python ams2.py [-h] [--freq FREQ] [--saveraw] [--loadraw LOADRAW]

    options:
        -h, --help         show this help message and exit
        --freq FREQ        frequency (Hz) to collect samples
        --saveraw          save raw samples
        --loadraw LOADRAW  load raw samples

# Raw samples

The base logger supports saving the raw samples to an sqlite3 db under `logs/raw` for later analysis or playback.  These files can get pretty large over extended sessions.
There is a RawSampler which can read in an sqlite3 db and 'replay' the samples through a logger to allow offline development or debugging.
The current loggers support this via the `--loadraw` parameter e.g.

    python ams2.py --loadraw logs/raw/ams2/1679937106.db

# Architecture

Sampler -> Logger -> MoTeC

- Sampler collects the raw UDP/Memory packets from the SIM and queues them
- Logger converts and saves samples and decides if a new session/log is to be created, optionally saving the raw samples for later playback
- MoTeC creates a MoTeC ld and ldx file from the collected samples and laptimes

Sampler and Logger are Sim specific, but they have BaseSampler and BaseLogger to handle the core loops and common functions like adding samples,
saving a log file and starting a new one

# Tests

    python -m unittest discover -v -s stm -p '*_test.py'

# TODO

* port AC UDP logger from https://github.com/GeekyDeaks/raw-sim-telemetry

# References / Kudos

- GT7 telemetry decode https://github.com/snipem/gt7dashboard 
- Salsa20 https://github.com/oconnor663/pure_python_salsa_chacha
- GT7 DB Files: https://github.com/ddm999/gt7info