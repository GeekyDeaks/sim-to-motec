from xml.dom import minidom

class MotecLogExtra:
    
    def __init__(self):
        self.laps = []

    def add_lap(self, laptime=None, lapnum=None):
        if lapnum:
            self.laps[lapnum] = laptime
        else:
            self.laps.append(laptime)
        
    def get_fastest_lap(self):

        if len(self.laps) < 1:
            return ( None, None )
        
        laps = self.laps
        if len(laps) > 1:
            # ignore the outlap
            laps = laps[:1]
            fastestlap, fastesttime =  sorted(enumerate(laps), key=lambda a: float(a[1]))[0]

            fastestlap += 2 # we removed the outlap and also index from 0
            return (fastestlap, fastesttime)
        else:
            # just return the one lap we have
            return ( 1, laps[0] )
    
    def get_beacons(self):

        beacons = []
        elapsedtime = 0

        for (idx, laptime) in enumerate(self.laps):
            elapsedtime += laptime * 1000000 # micro seconds
            beacons.append( (idx + 1, elapsedtime) )
    
        return beacons


    def to_string(self):

        root = minidom.Document()

        ldx = root.createElement("LDXFile")
        root.appendChild(ldx)

        ldx.setAttribute("locale", "English_United Kingdom.1252")
        ldx.setAttribute("DefaultLocale", "C")
        ldx.setAttribute("Version", "1.6")

        layers = root.createElement("Layers")
        ldx.appendChild(layers)

        layer = root.createElement("Layer")
        layers.appendChild(layer)

        markerblock = root.createElement("MarkerBlock")
        layer.appendChild(markerblock)

        markergroup = root.createElement("MarkerGroup")
        markerblock.appendChild(markergroup)
        markergroup.setAttribute("Name", "Beacons")
        markergroup.setAttribute("Index", str(len(self.laps) - 1)) # number of beacons 0 index

        for (lapnum, elapsedtime) in self.get_beacons():
            marker = root.createElement("Marker")
            marker.setAttribute("Version", "100")
            marker.setAttribute("ClassName", "BCN")
            marker.setAttribute("Name", f"Manual.{lapnum}")
            marker.setAttribute("Flags", "77")
            marker.setAttribute("Time", f"{elapsedtime:0.2f}")
            markergroup.appendChild(marker)

        details = root.createElement("Details")
        layers.appendChild(details)

        totallaps = root.createElement("String")
        details.appendChild(totallaps)
        totallaps.setAttribute("Id", "Total Laps")
        totallaps.setAttribute("Value", str(len(self.laps) + 1)) # include the in-lap

        fastestlap, fastesttime = self.get_fastest_lap()
        if fastesttime:
            minutes = int(fastesttime % 3600 // 60)
            seconds = fastesttime % 3600 % 60
            fastesttime = f"{minutes:02d}:{seconds:06.3f}"

            ft = root.createElement("String")
            details.appendChild(ft)
            ft.setAttribute("Id", "Fastest Time")
            ft.setAttribute("Value", fastesttime)

            fl = root.createElement("String")
            details.appendChild(fl)
            fl.setAttribute("Id", "Fastest Lap")
            fl.setAttribute("Value", str(fastestlap))

        return(root.toprettyxml(indent="  "))