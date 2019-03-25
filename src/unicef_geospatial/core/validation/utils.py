from math import atan2, cos, radians, sin, sqrt


def getval(ft, field):
    result = ""
    if field:
        val = ft[field]
        if val:
            if isinstance(val, str):
                result = "{}".format(val.encode('UTF-8').strip())
            else:
                result = "{}".format(val)
    return result


def calc_distance(lat1dd, lon1dd, lat2dd, lon2dd):
    # approximate radius of earth in m
    R = 6373.0

    lat1 = radians(lat1dd)
    lon1 = radians(lon1dd)
    lat2 = radians(lat2dd)
    lon2 = radians(lon2dd)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = (R * c) * 1000
    return distance
