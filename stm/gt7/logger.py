from stm.logger import BaseLogger
from stm.event import STMEvent
import stm.gps as gps

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

        if sample.current_lap < 0:
            self.last_lap = None
            return

        if self.last_lap is None:
            self.lap_samples = 0
            self.last_lap = sample.current_lap
            self.new_log(channels=self.channels, event=self.event)

        if sample.current_lap < self.last_lap:
            # start a new log
            self.new_log(channels=self.channels, event=self.event)

        if sample.current_lap != self.last_lap:
            # figure out the laptimes
            if sample.last_laptime > 0:
                self.add_lap(sample.last_laptime / 1000.0)
            else:
                # guess it from the number of samples
                self.add_lap(lap_samples / self.freq)
            lap_samples = 0
        else:
            lap_samples += 1


        self.last_lap = sample.current_lap

        # do some conversions
        # gear, throttle, brake, speed, z, x
        lat, long = gps.convert(x=sample.positionX, z=-sample.positionZ)
        self.add_samples([
            sample.gear & 0x0f,
            sample.throttle * 100 / 255,
            sample.brake * 100 / 255,
            sample.speed * 2.23693629, # m/s to mph
            lat,
            long
        ])

        if (sample.tick % 100) == 0:
            print(
                f"{timestamp:6} tick: {sample.tick:6}"
                f" {sample.positionX:10.5f} {sample.positionY:10.5f} {sample.positionZ:10.5f}"
                f" {sample.speed:3.0f} {sample.current_lap:2}/{sample.laps:2}"
                f" {sample.best_laptime:6}/{sample.last_laptime:6}"
                f" {sample.race_position:3}/{sample.opponents:3}"
                f" {sample.gear & 0x0f} {sample.throttle:3} {sample.brake:3}"
                f" {sample.car_code:5}"
            )

