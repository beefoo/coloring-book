# -*- coding: utf-8 -*-

import math
import matplotlib.path as mplPath
import numpy as np
from polysimplify import VWSimplifier
from scipy.ndimage import gaussian_filter1d

def containsPoint(points, point):
    bbPath = mplPath.Path(np.array(points))
    return bbPath.contains_point(point)

# Mean of list
def mean(data):
    n = len(data)
    if n < 1:
        return 0
    else:
        return sum(data) / n

def oscillate(p, amount, f=2.0):
    radians = p * (math.pi * f)
    m = math.sin(radians)
    return m * amount

# http://stackoverflow.com/a/30408825
def polygonArea(points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def radiansBetweenPoints(p1, p2):
    deltaX = p2[0] - p1[0]
    deltaY = p2[1] - p1[1]
    return math.atan2(deltaY, deltaX)

def roundToNearest(x, nearest):
    return round(1.0 * x / nearest) * nearest

def roundToNearestDegree(radians, degree):
    return math.radians(roundToNearest(math.degrees(radians), degree))

# for line simplification
def simplify(line, targetLength=100):
    simplifier = VWSimplifier(line)
    simplified = simplifier.from_number(targetLength)
    return simplified.tolist()

def smoothPoints(points, resolution=3, sigma=1.8):
    a = np.array(points)

    x, y = a.T
    t = np.linspace(0, 1, len(x))
    t2 = np.linspace(0, 1, len(y)*resolution)

    x2 = np.interp(t2, t, x)
    y2 = np.interp(t2, t, y)

    x3 = gaussian_filter1d(x2, sigma)
    y3 = gaussian_filter1d(y2, sigma)

    x4 = np.interp(t, t2, x3)
    y4 = np.interp(t, t2, y3)

    return zip(x4, y4)

def translatePoint(p, radians, distance):
    x2 = p[0] + distance * math.cos(radians)
    y2 = p[1] + distance * math.sin(radians)
    return (x2, y2)
