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
        self.rawfile = rawfile
        self.cur = None

    def execute_sql(self, sql, params):
        if not self.rawfile:
            return
        
        if not self.cur:
            l.info(f"writing raw samples to {self.rawfile}")
            os.makedirs(os.path.dirname(self.rawfile), exist_ok=True)
            con = sqlite3.connect(self.rawfile, isolation_level="IMMEDIATE")
            self.cur = con.cursor()
            self.cur.execute("CREATE TABLE samples(timestamp float, data blob)")
            self.cur.execute("CREATE TABLE settings(name, value)")

        return self.cur.execute(sql, params)

    def save_settings(self, settings):
        for setting in settings.items():
            self.execute_sql("INSERT INTO settings(name, value) values (?, ?)", setting )

    def get(self, timeout=None):
        return self.samples.get(timeout=timeout)

    def put(self, sample):
        self.samples.put(sample, block=False)
        self.execute_sql("INSERT INTO samples(timestamp, data) VALUES (?, ?)", sample)

    def stop(self):
        l.warn("stopping sampler")
        self.running = False

class RawSampler(Thread):

    def __init__(self, rawfile=None):
        super().__init__()
        self.samples = Queue(maxsize=1)
        self.running = False
        self.rawfile = rawfile
        self.freq = None # get the freq from the sample file

    def run(self):
        self.running = True
        con = sqlite3.connect(self.rawfile, isolation_level=None)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM samples ORDER BY timestamp")

        while self.running:

            try:
                timestamp, data = next(res)
                if isinstance(timestamp, int):
                    timestamp = timestamp / 1000.0
                self.samples.put( (timestamp, data), block=True )
            except:
                self.running = False

        con.close()

    def get(self, timeout=None):
        return self.samples.get(timeout=timeout)
    
    def stop(self):
        l.warn("stopping sampler")
        self.running = False
