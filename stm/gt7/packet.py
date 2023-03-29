try:
    from salsa20 import Salsa20_xor
except:
    from .pure_salsa20 import Salsa20_xor

import struct

class GT7DataPacket:

    fmt = struct.Struct(
        "<"
        "4x" # MAGIC / i / 4x
        "3f" # POSITION / 3f / 12x
        "12x" # VELOCITY / 3f / 12x
        "12x" # ROTATION / 3f / 12x
        "4x" # ROTATION_NORTH / f / 4x
        "12x" # VELOCITY_ANGULAR / 3f / 12x
        "4x" # RIDE_HEIGHT / f / 4x
        "f" # RPM / f / 4x
        "8x" # IV / 8B / 8x
        "4x" # UNKNOWN_0x48 / f / 4x
        "f" # SPEED / f / 4x
        "4x" # TURBO_BOOST / f / 4x
        "4x" # OIL_PRESSURE / f / 4x
        "4x" # UNKNOWN_0x58 / f / 4x
        "4x" # UNKNOWN_0x5C / f / 4x
        "16x" # TYRES_TEMP / 4f / 16x
        "i" # TICK / i / 4x
        "2h" # LAPS / 2H / 4x
        "i" # BEST_LAPTIME / i / 4x
        "i" # LAST_LAPTIME / i / 4x
        "4x" # DAYTIME_PROGRESSION / i / 4x
        "2h" # RACE_POSITION / 2H / 4x
        "8x" # ALERTS / 4H / 8x
        "B" # GEAR / B / x
        "B" # THROTTLE / B / x
        "B" # BRAKE / B / x
        "x" # UNKNOWN_0x92 / B / x
        "16x" # WHEELS_SPEED / 4f / 16x
        "16x" # TYRES_RADIUS / 4f / 16x
        "16x" # TYRE_SUSPENSION_TRAVEL / 4f / 16x
        "16x" # UNKNOWN / 4f / 16x
        "32x" # UNKNOWN_RESRVED / 32B / 32x
        "4x" # CLUCH / f / 4x
        "4x" # CLUCH_ENGAGEMENT / f / 4x
        "4x" # CLUCH_RPM / f / 4x
        "4x" # UNKNOWN_GEAR / f / 4x
        "32x" # UNKNOWN_GEAR_RATIO / 8f / 32x
        "I" # CAR_CODE / i / 4x
    )

    size = fmt.size

    def __init__(self, buf, encrypted=True):

        if encrypted:
            buf = self.decrypt(buf)

        (
            self.positionX,
            self.positionY,
            self.positionZ,
            self.rpm,
            self.speed,
            self.tick,
            self.current_lap,
            self.laps,
            self.best_laptime,
            self.last_laptime,
            self.race_position,
            self.opponents,
            self.gear,
            self.throttle,
            self.brake,
            self.car_code
        )  = self.fmt.unpack(buf)


    @staticmethod
    def decrypt(dat):
        KEY = b'Simulator Interface Packet GT7 ver 0.0'
        oiv = dat[0x40:0x44]
        iv1 = int.from_bytes(oiv, byteorder='little')
        iv2 = iv1 ^ 0xDEADBEAF 
        IV = bytearray()
        IV.extend(iv2.to_bytes(4, 'little'))
        IV.extend(iv1.to_bytes(4, 'little'))
        ddata = Salsa20_xor(dat, bytes(IV), KEY[0:32])

        #check magic number
        magic = int.from_bytes(ddata[0:4], byteorder='little')
        if magic != 0x47375330:
            return bytearray(b'')
        return ddata