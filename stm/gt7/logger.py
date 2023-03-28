from stm.logger import BaseLogger
from stm.event import STMEvent
import stm.gps as gps
from datetime import datetime
from .packet import GT7DataPacket
from .db.cars import lookup_car_name
from logging import getLogger
l = getLogger(__name__)

class GT7Logger(BaseLogger):

    channels = ['gear', 'throttle', 'brake', 'speed', 'lat', 'long']

    def __init__(self, 
                sampler=None,
                filetemplate=None,
                name="",
                session="",
                vehicle="",
                driver="",
                venue="", 
                comment="",
                shortcomment="",
                freq=None ):
        super().__init__(sampler=sampler, filetemplate=filetemplate, freq=60) # fixed freq for now

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
        self.last_tick = None

    def process_sample(self, timestamp, sample):

        new_log = False
        p = GT7DataPacket(sample)

        if p.current_lap < 0:
            self.last_lap = None
            self.save_log()
            return

        if self.last_lap is None:
            self.lap_samples = 0
            self.last_lap = p.current_lap
            self.last_tick = p.tick
            new_log = True

        if p.current_lap < self.last_lap:
            self.save_log()
            new_log = True

        if new_log:
            then = datetime.fromtimestamp(timestamp)
            if self.event.vehicle:
                vehicle = self.event.vehicle
            else:
                vehicle = lookup_car_name(p.car_code)

            event = STMEvent(
                name=self.event.name,
                session=self.event.session,
                vehicle=vehicle,
                driver=self.event.driver,
                venue=self.event.venue,
                comment=self.event.comment,
                shortcomment=self.event.shortcomment,
                date = then.strftime('%d/%m/%Y'),
                time = then.strftime('%H:%M:%S')
            )
            self.new_log(channels=self.channels, event=event)

        if p.current_lap > self.last_lap:
            # figure out the laptimes
            sampletime = self.lap_samples / self.freq
            if p.last_laptime > 0:
                laptime = p.last_laptime / 1000.0
            else:
                # guess it from the number of samples
                laptime = sampletime

            self.add_lap(laptime)
            l.info(f"adding lap {self.last_lap}, laptime: {laptime:.3f}, samples: {self.lap_samples}, sampletime: {sampletime:.3f}")
            self.lap_samples = 0
        else:
            self.lap_samples += 1

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

        missing_ticks = p.tick - (self.last_tick + 1)

        if missing_ticks > 0:
            l.warn(f"missed {missing_ticks} ticks, padding")
            # pad the missing ticks
            for t in range(missing_ticks):
                self.add_samples([
                    p.gear & 0x0f,
                    p.throttle * 100 / 255,
                    p.brake * 100 / 255,
                    p.speed * 2.23693629, # m/s to mph
                    lat,
                    long
                ])
                self.lap_samples += 1

        if (p.tick % 1000) == 0 or new_log:
            l.info(
                f"{timestamp:13.3f} tick: {p.tick:6}"
                f" {p.current_lap:2}/{p.laps:2}"
                f" {p.positionX:10.5f} {p.positionY:10.5f} {p.positionZ:10.5f}"
                f" {p.best_laptime:6}/{p.last_laptime:6}"
                f" {p.race_position:3}/{p.opponents:3}"
                f" {p.gear & 0x0f} {p.throttle:3} {p.brake:3} {p.speed:3.0f}"
                f" {p.car_code:5}"
            )



        self.last_lap = p.current_lap
        self.last_tick = p.tick

