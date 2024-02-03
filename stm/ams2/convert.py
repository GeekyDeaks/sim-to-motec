from stm.maths import Vector
import math

def convert_orientation(o):

    # convert AMS2 orientation radians to +/-180 deg

    y = math.pi + o.y if o.y < 0 else o.y - math.pi

    v = Vector(
        math.degrees(o.x),
        math.degrees(y),
        math.degrees(o.z)
    )

    return v