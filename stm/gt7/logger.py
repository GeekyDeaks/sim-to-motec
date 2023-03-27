from stm.logger import BaseLogger
from stm.event import STMEvent
import stm.gps as gps
from .packet import GT7DataPacket
from logging import getLogger
l = getLogger(__name__)

class GT7Logger(BaseLogger):

    channels = ['gear', 'throttle', 'brake', 'speed', 'lat', 'long']
    freq = 60 # fixed frequency for now

    def __init__(self, 
                sampler=None,
                filetemplate=None,
                name=None,
                session=None,
                vehicle=None,
                driver=None,
                venue=None, 
                comment=None,
                shortcomment=None,
                freq=None ):
        super().__init__(sampler=sampler, filetemplate=filetemplate)

        self.event = STMEvent(
            name=name,
            session=session,
            vehicle=vehicle,
            driver=driver,
            venue=venue,
            comment=comment,
            shortcomment=shortcomment
        )

        self.last_lap = None
        self.lap_samples = 0

    def process_sample(self, timestamp, sample):

        new_log = False
        p = GT7DataPacket(sample)

        if p.current_lap < 0:
            self.last_lap = None
            return

        if self.last_lap is None:
            self.lap_samples = 0
            self.last_lap = p.current_lap
            new_log = True

        if p.current_lap < self.last_lap:
            new_log = True

        if new_log:
            self.new_log(channels=self.channels, event=self.event)

        if p.current_lap != self.last_lap:
            # figure out the laptimes
            if p.last_laptime > 0:
                self.add_lap(p.last_laptime / 1000.0)
            else:
                # guess it from the number of samples
                self.add_lap(lap_samples / self.freq)
            lap_samples = 0
        else:
            lap_samples += 1


        self.last_lap = p.current_lap

        # do some conversions
        # gear, throttle, brake, speed, z, x
        lat, long = gps.convert(x=p.positionX, z=-p.positionZ)
        self.add_samples([
            p.gear & 0x0f,
            p.throttle * 100 / 255,
            p.brake * 100 / 255,
            p.speed * 2.23693629, # m/s to mph
            lat,
            long
        ])

        if (p.tick % 100) == 0:
            l.info(
                f"{timestamp:6} tick: {p.tick:6}"
                f" {p.positionX:10.5f} {p.positionY:10.5f} {p.positionZ:10.5f}"
                f" {p.speed:3.0f} {p.current_lap:2}/{p.laps:2}"
                f" {p.best_laptime:6}/{p.last_laptime:6}"
                f" {p.race_position:3}/{p.opponents:3}"
                f" {p.gear & 0x0f} {p.throttle:3} {p.brake:3}"
                f" {p.car_code:5}"
            )

