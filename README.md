# sim-to-motec

Simple sim telemetry to MoTeC log conversion

# getting started

    python3 -m venv py
    source py/bin/activate
    pip install -r requirements.txt

# GT7

    python gt7.py <IP Address of PS> --driver <DRIVER NAME> --venue <TRACK NAME>

# AMS2

    python ams2.py

# architecture

Sampler -> Logger -> MoTeC

- Sampler collects the raw UDP/Memory packets from the SIM and queues them, optionally saving the raw samples for later playback
- Logger converts and saves samples and decides if a new session/log is to be created
- MoTeC creates a MoTeC ld and ldx file from the collected samples and laptimes

Sampler and Logger are Sim specific, but they have BaseSampler and BaseLogger to handle the core loops and common functions like adding samples,
saving a log file and starting a new one

# tests

    python -m unittest discover -v -s stm -p '*_test.py'

# TODO

* port AC UDP logger from https://github.com/GeekyDeaks/raw-sim-telemetry