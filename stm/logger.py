from queue import Empty
from .motec import MotecLog, MotecLogExtra, MotecEvent
from .channels import get_channel_definition
import os
import re
import sqlite3
from logging import getLogger
l = getLogger(__name__)

class BaseLogger:

    def __init__(self, sampler=None, filetemplate=None, rawfile=None):
        self.sampler = sampler
        self.filetemplate = filetemplate
        self.log = None
        self.rawfile = rawfile

    def start(self):

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

        while self.sampler.is_alive():

            # wait for new samples
            try:
                timestamp, sample = self.sampler.get(timeout = 1 ) # to allow windows to use CTRL+C
                if cur:
                    cur.execute("INSERT INTO samples(timestamp, data) VALUES (?, ?)", ( timestamp, sample ))
                self.process_sample(timestamp, sample)

            except Empty:
                pass

            except KeyboardInterrupt:
                l.warn("stopping")
                break

            except Exception as e:
                # might have been something in the processing that triggered the exception
                # so let's see if we can save it for later
                if con:
                    con.commit()
                
                # keep going?
                raise e
                #l.error(e)

        if con:
            con.commit()
        self.save_log()
        self.sampler.stop()
        self.sampler.join()

    def active_log(self):
        return self.log is not None

    def new_log(self, event=None, channels=None):
        if self.log:
            self.save_log()

        template_vars = {}
        for k, v in vars(event).items():
            if v is not None:
                v = str(v).replace(' ', '_')
                v = re.sub(r'(?u)[^-\w.]', '', v)
            else: 
                v = ""

            template_vars[k] = v

        filename = self.filetemplate.format(**template_vars)
        filename = re.sub(r'_+', '_', filename)
        self.filename = re.sub(r'/_', '/', filename)

        l.info(f"starting new log {self.filename}")

        self.log = MotecLog({
            "date": event.date,
            "time": event.time,
            "driver": event.driver,
            "vehicle": event.vehicle,
            "venue": event.venue,
            "comment":event.shortcomment,
            "event": MotecEvent({
                "name": event.name,
                "session": event.session,
                "comment": event.comment,
                "venuepos": 0
            })
        })

        self.logx = MotecLogExtra()
        # add the channels

        for channel in channels:
            cd = get_channel_definition(channel, self.sampler.freq)
            self.log.add_channel(cd)

    def add_samples(self, samples):
        self.log.add_samples(samples)

    def add_lap(self, laptime=None, lap_num=None, samples=None, freq=None):
        # sanity check the lap vs samples
        if samples and freq:
            sample_time = samples / freq
            # check we have a sensible laptime for the number of samples
            if not laptime:
                laptime = sample_time
            elif laptime > 0 and abs(sample_time - laptime) > (2 / freq):
                # just use the sample_time
                l.warning(f"lap {lap_num}, ignoring time {laptime:.3f} as too far from sample period {sample_time:.3f}")
                laptime = sample_time

            l.info(f"adding lap {lap_num}, laptime: {laptime:.3f},"
                    f" samples: {samples}, sample_time: {sample_time:.3f}")

        self.logx.add_lap(laptime)

    def save_log(self):

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
            l.warn(f"aborting log {self.filename}, not enough laps")

        self.log = None