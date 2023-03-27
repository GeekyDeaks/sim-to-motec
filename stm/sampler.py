from threading import Thread
from queue import Queue
import sqlite3
import os
from logging import getLogger
l = getLogger(__name__)

class BaseSampler(Thread):

    def __init__(self, rawfile=None):
        super().__init__()
        self.samples = Queue()
        self.running = False
        if rawfile:
            l.info(f"writing raw samples to {rawfile}")
            os.makedirs(os.path.dirname(rawfile), exist_ok=True)
            self.con = sqlite3.connect(rawfile, isolation_level="IMMEDIATE")
            self.cur = self.con.cursor()
            self.cur.execute("CREATE TABLE samples(timestamp float, data blob)")
            self.cur.execute("CREATE TABLE settings(name, value)")
        else:
            self.con = None
            self.cur = None

    def save_settings(self, settings):
        if not self.cur:
            return
        
        for setting in settings.items():
            self.cur.execute("INSERT INTO settings(name, value) values (?, ?)", setting )


    def get(self, timeout=None):
        return self.samples.get(timeout=timeout)

    def put(self, sample):
        self.samples.put(sample, block=False)
        if self.cur:
            self.cur.execute("INSERT INTO samples(timestamp, data) VALUES (?, ?)", sample)


    def stop(self):
        l.warn("stopping sampler")
        self.running = False
        if self.con:
            self.con.close()