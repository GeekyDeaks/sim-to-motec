class MotecLogExtra:
    
    def __init__(self):
        self.laps = []

    def add_lap(self, laptime=None, lapnum=None):
        if lapnum:
            self.laps[lapnum] = laptime
        else:
            self.laps.append(laptime)
        
    def get_fastest_lap(self):

        if len(self.laps) < 2:
            return ( None, None )
        
        laps_without_outlap = self.laps[1:]
        fastestlap, fastesttime =  sorted(enumerate(laps_without_outlap), key=lambda a: float(a[1]))[0]

        fastestlap += 2 # we removed the outlap and also index from 0
        return (fastestlap, fastesttime)
    
    def get_beacons(self):

        beacons = []
        elapsedtime = 0

        for (idx, laptime) in enumerate(self.laps):
            elapsedtime += laptime * 1000000 # micro seconds
            beacons.append( (idx + 1, elapsedtime) )
    
        return beacons


    def to_string(self):

        markers = []
        for (marker, elapsedtime) in self.get_beacons():
            m = f"""        <Marker Version="100" ClassName="BCN" Name="Manual.{marker}" Flags="77" Time="{elapsedtime}"/>"""
            markers.append(m)


        beacons = len(markers) - 1
        totallaps = len(markers) + 1 # count the in lap

        fastestlap, fastesttime = self.get_fastest_lap()
        minutes = int(fastesttime % 3600 // 60)
        seconds = fastesttime % 3600 % 60
        fastesttime = f"{minutes:02d}:{seconds:06.3f}"
        xmllines = [
            """<?xml version="1.0"?>""",
            """<LDXFile Locale="English_United Kingdom.1252" DefaultLocale="C" Version="1.6">"""
            """<Layers>""",
            """  <Layer>""",
            """    <MarkerBlock>""",
           f"""      <MarkerGroup Name="Beacons" Index="{beacons}">""",
            *markers,
            """      </MarkerGroup>""",
            """    </MarkerBlock>""",
            """    <RangeBlock/>""",
            """  </Layer>""",
            """  <Details>""",
           f"""    <String Id="Total Laps" Value="{totallaps}"/>""",
           f"""    <String Id="Fastest Time" Value="{fastesttime}"/>""",
           f"""    <String Id="Fastest Lap" Value="{fastestlap}"/>""",
            """  </Details>""",
            """</Layers>""",
            """</LDXFile>"""
        ]
        return("\n".join(xmllines))