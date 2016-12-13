# -*- coding: utf-8 -*-

import math
import numpy as np
from polysimplify import VWSimplifier
from scipy.ndimage import gaussian_filter1d

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
