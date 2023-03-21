import math

def convert(x=None, z=None, latmid=52.83067304956695, longmid=-1.3740268265085214):

    # we consider lat to be z
    # therefore long x

    # https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree

    latmid_rad = math.radians(latmid)
    longmid_rad = math.radians(longmid)

    m_per_deg_lat = 111132.954 - (559.822 * math.cos( 2 * latmid_rad ) ) + ( 1.175 * math.cos( 4 * latmid_rad) ) - ( 0.0023 * math.cos( 6 * latmid_rad ))
    m_per_deg_lon = ( 111412.84 * math.cos( latmid_rad ) ) - (93.5 * math.cos( 3 * latmid_rad )) + (0.118 * math.cos( 5 * latmid_rad ))

    # z is lat, x is long
    dlat = z / m_per_deg_lat
    dlong = x / m_per_deg_lon

    lat = latmid + dlat
    long = longmid + dlong

    return (lat, long)