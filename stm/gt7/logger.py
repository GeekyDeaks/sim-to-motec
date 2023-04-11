from stm.logger import BaseLogger
from stm.event import STMEvent
import stm.gps as gps
from datetime import datetime
from copy import copy
from .packet import GT7DataPacket
from .db.cars import lookup_car_name
from .db.tracks import GT7TrackDetector
from logging import getLogger
l = getLogger(__name__)

class GT7Logger(BaseLogger):

    channels = ['beacon', 'lap', 'rpm', 'gear', 'throttle', 'brake', 'speed', 'lat', 'long',
                'velx', 'vely', 'velz', 'glat', 'gvert', 'glong', 
                'suspfl', 'suspfr', 'susprl', 'susprr',
                'wspdfl', 'wspdfr', 'wspdrl', 'wspdrr',
                'tyretempfl', 'tyretempfr', 'tyretemprl', 'tyretemprr',
                ]

    def __init__(self,
                rawfile=None,
                sampler=None,
                filetemplate=None,
                name="",
                session="",
                vehicle="",
                driver="",
                venue="", 
                comment="",
                shortcomment=""):
        super().__init__(rawfile=rawfile, sampler=sampler, filetemplate=filetemplate)

        self.event = STMEvent(
            name=name,
            session=session,
            vehicle=vehicle,
            driver=driver,
            venue=venue,
            comment=comment,
            shortcomment=shortcomment
        )

        self.current_event = None

        self.last_packet = None
        self.skip_samples = 0
        self.track = None
        self.track_detector = None

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

        freq = self.sampler.freq

        if currp.paused:
            return

        if not currp.in_race:
            self.save_log()
            return
        
        if currp.current_lap < lastp.current_lap:
            # possibly restarted the event
            self.save_log()

        if not self.log:
            self.track_detector = GT7TrackDetector()
            new_log = True
            self.skip_samples = 3
            then = datetime.fromtimestamp(timestamp)
            if self.event.vehicle:
                vehicle = self.event.vehicle
            else:
                vehicle = lookup_car_name(currp.car_code)

            event = copy(self.event)
            event.datetime = then.strftime("%Y-%m-%dT%H:%M:%S")
            event.vehicle = vehicle
            self.current_event = event
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
            laptime = currp.last_laptime / 1000.0
            self.add_lap(laptime=laptime, lap=lastp.current_lap)

            if not self.current_event.venue or self.track_detector.probability < .9:
                # try and guess the track
                self.track_detector.guess(lastp.position.x, lastp.position.z, currp.position.x, currp.position.z)

                if self.track_detector.track_name:
                    self.current_event.venue = self.track_detector.track_name
                    self.update_event(event=self.current_event)

        else:
            self.track_detector.update(currp.position.x, currp.position.z)

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

        # do some conversions
        # gear, throttle, brake, speed, z, x
        lat, long = gps.convert(x=currp.position.x, z=-currp.position.z)

        # mult the world deltav with the rotation to get local deltav
        deltav = (currp.velocity - lastp.velocity) * currp.rotation

        glat = deltav.x * freq / 9.8 # X
        gvert = deltav.y * freq / 9.8 # Y
        glong = deltav.z * freq / 9.8 # Z

        # calculate wheel speed (needs to be inverted)
        wheelspeed = [ r * s * -2.23693629 for r,s in zip(currp.wheelradius, currp.wheelspeed) ]

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
            *currp.suspension,
            *wheelspeed,
            *currp.tyretemp
        ])



