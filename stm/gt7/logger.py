from stm.logger import BaseLogger
from stm.event import STMEvent
import stm.gps as gps
from datetime import datetime
from copy import copy
from .packet import GT7DataPacket
from .db.cars import lookup_car_name
from logging import getLogger
l = getLogger(__name__)

class GT7Logger(BaseLogger):

    channels = ['beacon', 'lap', 'rpm', 'gear', 'throttle', 'brake', 'speed', 'lat', 'long',
                'velx', 'vely', 'velz', 'glat', 'gvert', 'glong', 
                'dposfl', 'dposfr', 'dposrl', 'dposrr']

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

        self.last_packet = None
        self.lap_samples = 0
        self.skip_samples = 0
        self.last_tick = None

    def process_sample(self, timestamp, sample):

        p = GT7DataPacket(sample)
        if not self.last_packet:
            self.last_packet = p

        # fill in any missing ticks
        missing = range(self.last_packet.tick + 1, p.tick)
        if len(missing):
            l.info(f"misssed {len(missing)} ticks, duplicating {self.last_packet.tick}")
            for tick in missing:
                # copy the currrent packet
                mp = copy(self.last_packet)
                mp.tick = tick
                self.process_packet(timestamp, mp)

        self.process_packet(timestamp, p)

        self.last_packet = p

    def process_packet(self, timestamp, packet):

        beacon = 0
        new_log = False

        lastp = self.last_packet
        currp = packet

        if currp.paused:
            return

        if not currp.in_race:
            self.save_log()
            return

        if not self.log:
            new_log = True
            self.lap_samples = 0
            self.skip_samples = 3
            then = datetime.fromtimestamp(timestamp)
            if self.event.vehicle:
                vehicle = self.event.vehicle
            else:
                vehicle = lookup_car_name(currp.car_code)

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

        if self.skip_samples > 0:
            l.info(f"skipping tick {currp.tick}")
            self.skip_samples -= 1
            return

        #if currp.current_lap < 1:
        #    return

        if currp.current_lap > lastp.current_lap:
            # figure out the laptimes
            beacon = 1
            sampletime = self.lap_samples / self.freq
            if currp.last_laptime > 0:
                laptime = currp.last_laptime / 1000.0
            else:
                # guess it from the number of samples
                laptime = sampletime

            self.add_lap(laptime)
            l.info(f"adding lap {lastp.current_lap}, laptime: {laptime:.3f}, samples: {self.lap_samples}, sampletime: {sampletime:.3f}")
            self.lap_samples = 0

        if (currp.tick % 1000) == 0 or new_log:
            l.info(
                f"{timestamp:13.3f} tick: {currp.tick:6}"
                f" {currp.current_lap:2}/{currp.laps:2}"
                f" {currp.position.x:10.5f} {currp.position.y:10.5f} {currp.position.z:10.5f}"
                f" {currp.best_laptime:6}/{currp.last_laptime:6}"
                f" {currp.race_position:3}/{currp.opponents:3}"
                f" {currp.gear} {currp.throttle:3} {currp.brake:3} {currp.speed:3.0f}"
                f" {currp.car_code:5}"
            )

        self.lap_samples += 1
        # do some conversions
        # gear, throttle, brake, speed, z, x
        lat, long = gps.convert(x=currp.position.x, z=-currp.position.z)

        # mult the world deltav with the rotation to get local deltav
        deltav = (currp.velocity - lastp.velocity) * currp.rotation

        glat = deltav.x * self.freq / 9.8 # X
        gvert = deltav.y * self.freq / 9.8 # Y
        glong = deltav.z * self.freq / 9.8 # Z

        self.add_samples([
            beacon,
            currp.current_lap,
            currp.rpm,
            currp.gear,
            currp.throttle * 100 / 255,
            currp.brake * 100 / 255,
            currp.speed * 2.23693629, # m/s to mph
            lat,
            long,
            deltav.x,
            deltav.y,
            -deltav.z, # so we match the GPS long,
            glat,
            gvert,
            -glong,
            *currp.suspension
        ])



