from threading import Thread
from queue import Queue
import sqlite3
from logging import getLogger
l = getLogger(__name__)

class BaseSampler(Thread):

    def __init__(self, freq=None):
        super().__init__()
        self.freq = freq
        self.samples = Queue()
        self.running = False

    def get(self, timeout=None):
        return self.samples.get(timeout=timeout)

    def put(self, sample):
        self.samples.put(sample, block=False)

    def stop(self):
        l.warning("stopping sampler")
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
        res = cur.execute("SELECT value FROM settings WHERE name='freq'")
        (self.freq, ) = res.fetchone()
        res = cur.execute("SELECT * FROM samples ORDER BY timestamp")

        last_data = None

        while self.running:

            try:
                timestamp, data = next(res)
                if isinstance(timestamp, int):
                    timestamp = timestamp / 1000.0

                if data is None:
                    # repeat the last changed sample
                    data = last_data
                else:
                    last_data = data

                self.samples.put( (timestamp, data), block=True )
            except:
                self.running = False

        con.close()

    def get(self, timeout=None):
        return self.samples.get(timeout=timeout)
    
    def stop(self):
        l.warning("stopping sampler")
        self.running = False
