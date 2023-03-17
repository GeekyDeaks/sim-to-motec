import struct
from pprint import pformat
import binascii

class MotecStruct:

    def __init__(self, fields):


        self.fmt = "<" + "".join([ f[0] for f in fields])
        self.size = struct.calcsize(self.fmt)
        self.fields = fields

    """
    unpack a binary string and return a dict of the values
    optionally add the padding values as binary strings for debugging
    """

    def unpack(self, data, pad = True):

        tup = struct.unpack(self.fmt, data)
        d = dict()

        padidx = 0
        for (idx, val) in enumerate(tup):

            (fmt, key) = self.fields[idx]

            if pad and not key:
                key = f"pad{padidx}"
                padidx += 1
                val = binascii.hexlify(val, sep="-", bytes_per_sep=8)
            elif fmt[-1] == "s":
                val = val.decode('utf-8').rstrip('\0')

            if key:
                d[key] = val
        return d
    

class MotecBase:

    def __init__(self, state = None):

        if isinstance(state, dict):
            # unpickle
            for (k, v) in state.items():
                setattr(self, k, v)

    def __disable_repr__(self):
        return pformat(vars(self), sort_dicts=False, compact=True, width=200)
    
    @classmethod
    def from_string(cls, data, start = 0, pad = False):
        pkt = data[start : cls.header.size + start] # get the part of the data we are interested in
        state = cls.header.unpack(pkt, pad=pad)
        state["_start"] = start
        return cls(state=state)

    
class MotecEvent(MotecBase):

    header = MotecStruct([
        ("64s", "name"),
        ("64s", "session"),
        ("1024s", "comment"),
        ("H", "venuepos")
    ])

class MotecChannel(MotecBase):

    header = MotecStruct([
        ("I", "prevpos"),
        ("I", "nextpos"),
        ("I", "datapos"),
        ("I", "numsamples"),
        ("2s", None),
        ("H", "datatype"),
        ("H", "datalen"),
        ("H", "freq"),
        ("h", "shift"),
        ("h", "multiplier"),
        ("h", "scale"),
        ("h", "decplaces"),
        ("32s", "name"),
        ("8s", "shortname"),
        ("12s", "units"),
        ("32s", None)
    ])

    @classmethod
    def from_string(cls, data, start = 0, pad = False):
        # the log has to start from zero
        channel = super().from_string(data, start=start, pad=pad)

        # determine the data type
        if channel.datatype in [ 7 ]:
            # float
            fmt = [ None, "e", None, "f" ][ channel.datalen - 1 ]

        elif channel.datatype in [ 3 ]:
            # int
            fmt = [ "b", "h", None, "i" ][ channel.datalen - 1 ]
        else:
            raise ValueError(f"unknown datatype {channel.datatype}")

        # go to the start of the data and unpack all the values
        values = []
        fmt_len = struct.calcsize(fmt)
        for i in range(channel.numsamples):
            # unpack the value
            pos = channel.datapos + ( i * fmt_len )
            d = data[pos:fmt_len + pos]
            ( v, ) = struct.unpack(fmt, d)
            v = (v / channel.scale * pow(10., -channel.decplaces) + channel.shift) * channel.multiplier

            values.append((v,  binascii.hexlify(d, sep="-", bytes_per_sep=8)))

        channel.values = values
        return channel
    

    def to_string(self):

        for v in self.values:
            v = ( (v / self.multiplier) - self.shift) * self.scale / pow(10.0, -self.decplaces)


class MotecLog(MotecBase):

    header = MotecStruct([
        (    "I", "id"),
        (   "4s", None),
        (    "I", "firstchannelpos"),
        (    "I", "firstchanneldatapos"),
        (  "20s", None),
        (    "I", "eventpos" ),
        (  "30s", None),
        (    "I", "serial"),
        (   "8s", "type"),
        (    "H", "version"),
        (   "2s", None),
        (    "I", "numchannels"),
        (   "4s", None),
        (  "16s", "date"),
        (  "16s", None),
        (  "16s", "time"),
        (  "16s", None),
        (  "64s", "driver"),
        (  "64s", "vehicle"),
        (  "64s", None),
        (  "64s", "venue"),
        ("1088s", None),
        (   "I" , "pro"),
        (  "66s", None),
        (  "64s", "comment"),
        ( "126s", None)
    ])

    @classmethod
    def from_string(cls, data, pad = False):
        # the log has to start from zero
        log = super().from_string(data, pad=pad)

        if log.eventpos:
            log.event = MotecEvent.from_string(data, start = log.eventpos, pad=pad)

        log.channels = []

        channelpos = log.firstchannelpos

        while channelpos:
            channel = MotecChannel.from_string(data, start = channelpos, pad=pad)
            log.channels.append(channel)
            channelpos = channel.nextpos

        return log
