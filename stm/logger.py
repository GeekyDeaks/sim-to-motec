from queue import Empty
from .motec import MotecLog, MotecLogExtra, MotecEvent
from .channels import get_channel_definition
import os
import re
from logging import getLogger
l = getLogger(__name__)

class BaseLogger:

    def __init__(self, sampler=None, filetemplate=None):
        self.sampler = sampler
        self.filetemplate = filetemplate
        self.log = None

    def start(self):

        l.info("starting logger")
        # start the sampler
        self.sampler.start()

        while self.sampler.is_alive():

            # wait for new samples
            try:
                timestamp, sample = self.sampler.get(timeout = 1 ) # to allow windows to use CTRL+C
                self.process_sample(timestamp, sample)

            except Empty:
                pass

            except KeyboardInterrupt:
                l.warn("stopping")
                break

        self.sampler.stop()
        self.sampler.join()

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
        self.filename = re.sub(r'_+', '_', filename)

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
            cd = get_channel_definition(channel)
            self.log.add_channel(cd)

    def add_samples(self, samples):
        self.log.add_samples(samples)

    def add_log(self, laptime):
        self.logx.add_lap(laptime)

    def save_log(self):

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