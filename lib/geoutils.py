# -*- coding: utf-8 -*-

import math
import matplotlib.path as mplPath
import numpy as np

def containsPoint(points, point):
    bbPath = mplPath.Path(np.array(points))
    return bbPath.contains_point(point)

def coordinateToPixel(lnglat, w, h, bounds):
    west = math.radians(bounds[0])
    south = math.radians(bounds[1])
    east = math.radians(bounds[2])
    north = math.radians(bounds[3])

    ymin = mercator(south)
    ymax = mercator(north)
    xFactor = 1.0 * w / (east - west)
    yFactor = 1.0 * h / (ymax - ymin)

    x = math.radians(lnglat[0])
    y = mercator(math.radians(lnglat[1]))
    x = (x - west) * xFactor
    y = (ymax - y) * yFactor # y points south
    return (x, y)

def getBounds(coordinates):
    lngs = []
    lats = []
    for coords in coordinates:
        for p in coords:
            lngs.append(p[0])
            lats.append(p[1])
    minLng = min(lngs)
    maxLng = max(lngs)
    minLat = min(lats)
    maxLat = max(lats)
    return (minLng, minLat, maxLng, maxLat)

def getRatio(coordinates):
    bounds = getBounds(coordinates)
    west = math.radians(bounds[0])
    south = math.radians(bounds[1])
    east = math.radians(bounds[2])
    north = math.radians(bounds[3])
    ymin = mercator(south)
    ymax = mercator(north)
    width = (east - west)
    height = (ymax - ymin)
    return (width, height)

def mercator(radians):
    return math.log(math.tan(radians*0.5 + math.pi*0.25))

def withinCoordinates(coords, p):
    within = False
    for c in coords:
        if containsPoint(c, p):
            within = True
            break
    return within
