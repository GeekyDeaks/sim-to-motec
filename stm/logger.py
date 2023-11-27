from threading import Thread
from queue import Empty
from .motec import MotecLog, MotecLogExtra, MotecEvent
from .channels import get_channel_definition
import os
import re
import sqlite3
from pathlib import Path
from datetime import datetime
from logging import getLogger
l = getLogger(__name__)

class BaseLogger(Thread):

    def __init__(self, sampler=None, filetemplate=None, rawfile=None, imperial=False):
        super().__init__()
        self.sampler = sampler
        self.filetemplate = filetemplate
        self.filename = None
        self.log = None
        self.rawfile = rawfile
        self.lap_samples = 0
        self.imperial = imperial

    def run(self):

        l.info("starting logger")

        cur = None
        con = None

        # sort out the raw db
        if self.rawfile:
            l.info(f"writing raw samples to {self.rawfile}")
            os.makedirs(os.path.dirname(self.rawfile), exist_ok=True)
            con = sqlite3.connect(self.rawfile, isolation_level="IMMEDIATE")
            cur = con.cursor()
            cur.execute("CREATE TABLE samples(timestamp float, data blob)")
            cur.execute("CREATE TABLE settings(name, value)")
            cur.execute("INSERT INTO settings(name, value) values (?, ?)", ("freq", self.sampler.freq) )
            con.commit()

        # start the sampler
        self.sampler.start()

        last_sample = b''

        while self.sampler.is_alive():

            # wait for new samples
            try:
                timestamp, sample = self.sampler.get(timeout = 1 ) # to allow windows to use CTRL+C
                if cur:
                    to_save = sample if sample != last_sample else None
                    cur.execute("INSERT INTO samples(timestamp, data) VALUES (?, ?)", ( timestamp, to_save ))
                self.process_sample(timestamp, sample)
                last_sample = sample

            except Empty:
                pass

            except Exception as e:
                # might have been something in the processing that triggered the exception
                # so let's see if we can save it for later
                if con:
                    con.commit()
                
                # keep going?
                raise e

        if con:
            con.commit()
        self.save_log()
        self.sampler.join()

    def active_log(self):
        return self.log is not None

    def new_log(self, event=None, channels=None):
        if self.log:
            self.save_log()

        self.log = MotecLog()
        self.update_event(event)

        l.info(f"starting new log {self.filename}")

        self.logx = MotecLogExtra()
        # add the channels

        for channel in channels:
            cd = get_channel_definition(channel, self.sampler.freq, self.imperial)
            self.log.add_channel(cd)

    def update_event(self, event=None):
        if not event or not self.log:
            return
        
        # convert the event datetime to MoTeC format
        dt = datetime.fromisoformat(event.datetime)
        self.log.date = dt.strftime('%d/%m/%Y')
        self.log.time = dt.strftime('%H:%M:%S')
        
        self.log.datetime = event.datetime
        self.log.driver = event.driver
        self.log.vehicle = event.vehicle
        self.log.venue = event.venue
        self.log.comment = event.shortcomment
        self.log.event = MotecEvent({
            "name": event.name,
            "session": event.session,
            "comment": event.comment,
            "venuepos": 0
        })

        template_vars = {}
        for k, v in vars(event).items():
            if v is not None:
                v = str(v).replace(' ', '_')
                v = re.sub(r'(?u)[^-\w.]', '', v)
            else: 
                v = ""

            template_vars[k] = v

        filepath = Path(self.filetemplate).parts
        # do substitution
        filepath = [ p.format(**template_vars) for p in filepath ]
        # sub out any invalid chars
        filepath = [ re.sub(r'[:/\\]+', '_', p ) for p in filepath ]
        # sub out any duplicate _
        filepath = [ re.sub(r'_+', '_', p) for p in filepath ]
        # sub out any leading or trailing _
        filepath = [ re.sub(r'^_|_$', '', p ) for p in filepath ]
        # remove any blank
        filepath = [ p for p in filepath if p ]
        self.filename = os.path.join(*filepath)

    def add_samples(self, samples):
        self.log.add_samples(samples)
        self.lap_samples += 1

    def add_lap(self, laptime=0.0, lap=None):

        samples = self.lap_samples
        freq = self.sampler.freq
        sample_time = samples / freq
        # check we have a sensible laptime for the number of samples
        if abs(sample_time - laptime) > (10 / freq):
            # just use the sample_time
            l.warning(f"lap {lap}, ignoring time {laptime:.3f} as too far from sample period {sample_time:.3f}")
            laptime = sample_time

        l.info(f"adding lap {lap}, laptime: {laptime:.3f},"
                f" samples: {samples}, sample_time: {sample_time:.3f}")

        self.logx.add_lap(laptime)
        self.lap_samples = 0

    def stop(self):
        if self.sampler:
            self.sampler.stop()

    def save_log(self):

        self.lap_samples = 0

        if not self.log:
            return
        
        # check if have at least 2 laps? out + pace
        if self.logx.valid_laps():


            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            # dump the ldx
            ldxfilename = f"{self.filename}.ldx"
            l.info(f"writing laptimes to {ldxfilename}")
            with open(ldxfilename, "w") as fout:
                fout.write(self.logx.to_string())

            # dump the log
            ldfilename = f"{self.filename}.ld"
            l.info(f"writing MoTeC log to {ldfilename}")
            with open(ldfilename, "wb") as fout:
                fout.write(self.log.to_string())
        else:
            l.warning(f"aborting log {self.filename}, not enough laps")

        self.log = None


    def get_venue(self):
        if self.log:
            return self.log.venue
        else:
            return ""
        
    def get_vehicle(self):
        if self.log:
            return self.log.vehicle
        else:
            return ""