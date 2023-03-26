# sim-to-motec

Simple sim telemetry to MoTeC log conversion

# getting started

    python3 -m venv py
    source py/bin/activate


# architecture

Sampler -> Logger -> Log

- Sampler collects the raw UDP/Memory packets from the SIM and queues them
- Logger converts samples and decides if a new session/log is to be created
- Log saves all samples until the session ends or the process is stopped and then saves them to a MoTeC log

Sample and Session are Sim specific

# tests

    python -m unittest discover -v -s stm -p '*_test.py'

# TODO

* port AC UDP logger from https://github.com/GeekyDeaks/raw-sim-telemetry
* port GT7 UDP logger from https://github.com/GeekyDeaks/raw-sim-telemetry
* finish AMS2 shared memory logger