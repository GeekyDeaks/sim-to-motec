from stm.sampler import BaseSampler
import time
from multiprocessing import shared_memory
from logging import getLogger
l = getLogger(__name__)

SHAREDMEM_NAME="$pcars2$"
DEFAULT_FREQ=20 # Hz

class AMS2Sampler(BaseSampler):

    def __init__(self, shmem_name=SHAREDMEM_NAME, freq=None):
        super().__init__()
        self.running = False
        self.shmem_name = shmem_name
        if not freq:
            freq = DEFAULT_FREQ
        self.freq = freq

    def run(self):

        self.running = True # this is set to False in BaseSampler when we are done
        wait = None
        shm_b = None

        while self.running:

            try:

                # try and get the shared memory
                if wait:
                    time.sleep(wait)

                now = time.time() # when

                if not shm_b:
                    shm_b = shared_memory.SharedMemory(self.shmem_name)
                    l.info("connected to AMS2 shared memory")
                    next_sample = now

                self.put(( now, shm_b.buf ))

                # work out when the next sample will be
                now = time.time()
                next_sample = max(next_sample + (1 / self.freq), now)
                wait = next_sample - now

            except FileNotFoundError:
                if wait is None:
                    l.info("waiting for AMS2 to start")
                wait = 1