import struct
import binascii
from io import BytesIO

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

        for (idx, val) in enumerate(tup):

            (fmt, key) = self.fields[idx]

            if pad and not key:
                key = f"pad{idx}"
                val = binascii.hexlify(val)
            elif key and fmt[-1] == "s":
                val = val.decode('utf-8').rstrip('\0')

            if key:
                d[key] = val
        return d
    

    def pack(self, state):

        # build a tuple for packing
        values = []
        for (idx, field) in enumerate(self.fields):
            fmt, key = field
            if not key:
                # make a pad key
                key = f"pad{idx}"
                # check if we have set the pad value
                # if so, use it
                if key in state:
                    values.append( binascii.unhexlify(state[key]) )
                else:
                    values.append(b"")

            elif fmt[-1] == "s":
                values.append(state[key].encode("utf-8"))
            else:
                values.append(state[key])
            
        return struct.pack(self.fmt, *values)


class MotecBase:

    def __init__(self, state = None):

        if isinstance(state, dict):
            # unpickle
            for (k, v) in state.items():
                setattr(self, k, v)
    
    @classmethod
    def from_string(cls, data, start = 0, pad = False):
        pkt = data[start : cls.header.size + start] # get the part of the data we are interested in
        state = cls.header.unpack(pkt, pad=pad)
        state["_start"] = start
        return cls(state=state)
    
    def to_string(self):
        return self.header.pack(vars(self))

class MotecEvent(MotecBase):

    header = MotecStruct([
        (  "64s", "name"),
        (  "64s", "session"),
        ("1024s", "comment"),
        (    "H", "venuepos")
    ])


class MotecSamples():

    datatypes = {
        0x0007: { # float
            0x0002: "e", # 2 byte float
            0x0004: "f", # 4 byte float
        },
        0x0003: { # int
            0x0001: "b", # 1 byte int
            0x0002: "h", # 2 byte int
            0x0004: "i", # 4 byte int
        }
    }

    converttypes = {
        0x0007: float,
        0x0003: int
    }

    def __init__(self, channel = None, samples = None):
        if samples:
            self.samples = samples
        else:
            self.samples = []

        self.channel = channel
        self.fmt = self.datatypes[channel.datatype][channel.datasize]
        self.convert = self.converttypes[channel.datatype]
        self.datasize = struct.calcsize(self.fmt)
        self.multiplier = channel.multiplier
        self.shift = channel.shift
        self.scale = channel.scale
        self.decplaces = channel.decplaces

    @property
    def numsamples(self):
        return len(self.samples)

    def add_sample(self, sample):
        self.samples.append(sample)

    def to_string(self):
        data = bytearray()
        for v in self.samples:
            v = ( (v / self.multiplier) - self.shift) * self.scale / pow(10.0, -self.decplaces)
            v = self.convert(v)
            data += struct.pack(self.fmt, v)

        return data

    @classmethod
    def from_string(cls, data, channel = None):

        if not channel:
            return

        samples = cls(channel=channel)

        # go to the start of the data and unpack all the values
        startpos = channel.datapos
        endpos = startpos + (samples.datasize * channel.numsamples)
        for (v, ) in struct.iter_unpack(samples.fmt, data[startpos:endpos]):
            v = (v / channel.scale * pow(10., -channel.decplaces) + channel.shift) * channel.multiplier
            samples.add_sample(v)

        return samples


class MotecChannel(MotecBase):

    header = MotecStruct([
        (  "I", "prevpos"),
        (  "I", "nextpos"),
        (  "I", "datapos"),
        (  "I", "numsamples"),
        (  "H", "id"),
        (  "H", "datatype"),
        (  "H", "datasize"),
        (  "H", "freq"),
        (  "h", "shift"),
        (  "h", "multiplier"),
        (  "h", "scale"),
        (  "h", "decplaces"),
        ("32s", "name"),
        ( "8s", "shortname"),
        ("12s", "units"),
        ("40s", None) # should only be 32
    ])

    def __init__(self, state):
        super().__init__(state)

        # check if we have any samples defined
        if not getattr(self, "samples", None):
            self.samples = MotecSamples(channel=self)

    def add_sample(self, sample):
        self.samples.add_sample(sample)

    def to_string(self):
        self.numsamples = self.samples.numsamples
        return super().to_string()

    @classmethod
    def from_string(cls, data, start = 0, pad = False):
        # the log has to start from zero
        channel = super().from_string(data, start=start, pad=pad)
        channel.samples = MotecSamples.from_string(data, channel)
        return channel

class MotecLog(MotecBase):

    header = MotecStruct([
        (    "I", "id"),
        (   "4s", None),
        (    "I", "firstchannelpos"),
        (    "I", "firstchanneldatapos"),
        (  "20s", None),
        (    "I", "eventpos" ),
        (  "26s", None),
        (    "I", "sig1"),
        (    "I", "serial"),
        (   "8s", "type"),
        (    "H", "version"),
        (    "H", "sig2"),
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
        (   "4s", None),
        (  "66s", None),
        (  "64s", "comment"),
        ( "126s", None)
    ])

    def __init__(self, state):
        super().__init__(state)
        if not getattr(self, "channels", None):
            self.channels = []
            self.numchannels = 0

        # we need these 'magics' to make it work, so set some defaults
        self.id = getattr(self, "id", 64)
        self.sig1 = getattr(self, "sig1", 1000000)
        self.sig2 = getattr(self, "sig2", 128)
        self.type = getattr(self, "type", "ADL")
        self.version = getattr(self, "version", 420)
        self.serial = getattr(self, "serial", 12007)

    def add_channel(self, channel):
        if not isinstance(channel, MotecChannel):
            channel = MotecChannel(channel)
        self.channels.append(channel)
        self.numchannels = len(self.channels)

    def add_samples(self, samples):
        for (idx, sample) in enumerate(samples):
            self.channels[idx].add_sample(sample)


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
            log.add_channel(channel)
            channelpos = channel.nextpos

        return log

    def to_string(self):

        data = BytesIO()

        # pack the event
        eventpos = 0
        nextpos = self.header.size
        if getattr(self, "event", None):
            eventpos = nextpos
            nextpos = nextpos + self.event.header.size
            data.seek(eventpos)
            data.write(self.event.to_string())
            
        self.eventpos = eventpos

        # work out the channel pointers
        self.firstchanneldatapos = 0
        self.firstchannelpos = 0

        if self.numchannels:

            # work out the first datapos
            datapos = nextpos + (MotecChannel.header.size * self.numchannels)
            self.firstchannelpos = nextpos
            self.firstchanneldatapos = datapos
            prevpos = 0
            thispos = nextpos

            for (idx, ci) in enumerate(self.channels):

                # work out where the next channel header will be
                if idx < (self.numchannels - 1):
                    ci.nextpos = thispos + ci.header.size
                else:
                    ci.nextpos = 0

                ci.prevpos = prevpos
                ci.datapos = datapos
                data.seek(thispos)
                data.write(ci.to_string())

                # get the samples for the channel
                samples = ci.samples.to_string()
                data.seek(datapos)
                data.write(samples)
                
                # finally, update all the pointers
                datapos += len(samples)
                prevpos = thispos
                thispos = ci.nextpos

        # now pack the log header
        data.seek(0)
        data.write(super().to_string())
        return data.getbuffer()