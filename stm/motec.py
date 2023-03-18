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
                val = binascii.hexlify(val, sep=" ", bytes_per_sep=4)
            elif fmt[-1] == "s":
                val = val.decode('utf-8').rstrip('\0')

            if key:
                d[key] = val
        return d
    

    def pack(self, state):

        # build a tuple for packing
        values = []
        for (fmt, key) in self.fields:
            if not key:
                values.append(b"")
            elif fmt[-1] == "s":
                values.append(state[key].encode("utf-8"))
            else:
                values.append(state[key])
            
        return struct.pack(self.fmt, *values)      
    

class MotecByteArray:
    def __init__(self, s = b''):
        self.buffer = bytearray(s)

    def update(self, pos, s):
        self.buffer += b"\x00" * (pos - len(self.buffer))
        self.buffer[pos:pos + len(s)] = s


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


    def add_sample(self, sample):
        samples = getattr(self, "samples", [])
        samples.append(sample)
        self.numsamples = len(samples)
        self.samples = samples


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

    convert = {
        0x0007: float,
        0x0003: int
    }

    @classmethod
    def from_string(cls, data, start = 0, pad = False):
        # the log has to start from zero
        channel = super().from_string(data, start=start, pad=pad)

        try:
            fmt = cls.datatypes[channel.datatype][channel.datasize]
        except:
            raise ValueError(f"unknown datatype 0x{channel.datatype:04X} / 0x{channel.datasize:04X}")

        # go to the start of the data and unpack all the values
        samples = []
        datasize = struct.calcsize(fmt)
        startpos = channel.datapos
        endpos = startpos + (datasize * channel.numsamples)
        channel._datasize = datasize
        for (v, ) in struct.iter_unpack(fmt, data[startpos:endpos]):
            v = (v / channel.scale * pow(10., -channel.decplaces) + channel.shift) * channel.multiplier
            samples.append(v)

        channel.samples = samples
        return channel
    

    def samples_to_string(self):
        data = bytearray()
        try:
            fmt = self.datatypes[self.datatype][self.datasize]
        except:
            raise ValueError(f"unknown datatype 0x{self.datatype:04X} / 0x{self.datasize:04X}")

        convert = self.convert[self.datatype]

        for v in self.samples:
            v = ( (v / self.multiplier) - self.shift) * self.scale / pow(10.0, -self.decplaces)
            v = convert(v)
            data += struct.pack(fmt, v)

        return data

class MotecLog(MotecBase):

    header = MotecStruct([
        (    "I", "id"),
        (   "4s", None),
        (    "I", "firstchannelpos"),
        (    "I", "firstchanneldatapos"),
        (  "20s", None),
        (    "I", "eventpos" ),
        (  "26s", None),
        (    "I", "sig1"), # not sure what this is? int value 1000000
        (    "I", "serial"),
        (   "8s", "type"),
        (    "H", "version"),
        (    "H", "sig2"), # another unknown, 128
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

    def __init__(self, state):
        super().__init__(state)

    def add_channel(self, channel_def):
        channels = getattr(self, "channels", [])
        channels.append(MotecChannel(channel_def))
        self.numchannels = len(channels)
        self.channels = channels

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
            log.channels.append(channel)
            channelpos = channel.nextpos

        return log

    def to_string(self):

        data = MotecByteArray()

        # pack the event
        eventpos = 0
        nextpos = self.header.size
        if getattr(self, "event", None):
            eventpos = nextpos
            nextpos = nextpos + self.event.header.size
            data.update(eventpos, self.event.to_string())
            
        self.eventpos = eventpos

        # work out the channel pointers
        self.firstchanneldatapos = 0
        self.firstchannelpos = 0

        self.id = 64

        # these are required for pro to work
        self.pro = 13764642
        self.sig1 = 1000000
        self.sig2 = 128

        self.type = "ADL"
        self.version = 420
        self.serial = 12007

        if self.numchannels:

            # fudge, bump nextpos ahead
            #nextpos = 13384

            # we can work out the first datapos
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
                data.update(thispos, ci.to_string())

                # get the samples for the channel
                samples = ci.samples_to_string()
                data.update(datapos, samples)
                
                # finall, update all the pointers
                datapos += len(samples)
                prevpos = thispos
                thispos = ci.nextpos

        # now pack the log header
        data.update(0, super().to_string())
        #data[self.eventpos:self.eventpos + self.event.header.size] = self.event.to_string()
        return data.buffer