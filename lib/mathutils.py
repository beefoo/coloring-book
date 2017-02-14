# -*- coding: utf-8 -*-

import math
import matplotlib.path as mplPath
import numpy as np
from polysimplify import VWSimplifier
from scipy.ndimage import gaussian_filter1d

def ceilToNearest(x, nearest):
    return math.ceil(1.0 * x / nearest) * nearest

def containsPoint(points, point):
    bbPath = mplPath.Path(np.array(points))
    return bbPath.contains_point(point)

def ellipseCircumference(a, b):
    t = ((a-b)/(a+b))**2
    return math.pi*(a+b)*(1 + 3*t/(10 + math.sqrt(4 - 3*t)))

def ellipseRadius(a, b, angle):
    r = math.radians(angle)
    return (a * b) / math.sqrt(a**2 * math.sin(r)**2 + b**2 * math.cos(r)**2)

def floorToNearest(x, nearest):
    return math.floor(1.0 * x / nearest) * nearest

def halton(index, base=3):
    result = 0
    f = 1.0 / base
    i = index
    while i > 0:
      result += f * float(i % base)
      i = math.floor(i / base)
      f = f / float(base)
    return result

def lerp(a, b, amount):
    return (b-a) * amount + a

def lerp2D(a, b, amount):
    x = a[0] + (b[0] - a[0]) * amount
    y = a[1] + (b[1] - a[1]) * amount
    return (x, y)

def lineIntersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('Lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return (x, y)

# Mean of list
def mean(data):
    n = len(data)
    if n < 1:
        return 0
    else:
        return sum(data) / n

def norm(value, a, b):
    return 1.0 * (value - a) / (b - a)

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

def scalePoints(points, scale):
    for i,p in enumerate(points):
        points[i] = (p[0]*scale, p[1]*scale)
    return points

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

def translatePoints(points, x, y):
    for i,p in enumerate(points):
        points[i] = (p[0]+x, p[1]+y)
    return points

def xIntersect(points, x):
    if len(points) < 2:
        raise Exception('Not enough points in line')
    pointsLeft = sorted([p for p in points if p[0] <= x], key=lambda point: abs(point[0]-x))
    pointsRight = sorted([p for p in points if p[0] > x], key=lambda point: abs(point[0]-x))
    # we have an exact match
    if len(pointsLeft) and pointsLeft[0][0] == x:
        return pointsLeft[0]
    # no intersection
    elif not len(pointsLeft) or not len(pointsRight):
        raise Exception('Lines do not intersect')
    y0 = min(pointsLeft[0][1], pointsRight[0][1]) - 1
    y1 = max(pointsLeft[0][1], pointsRight[0][1]) + 1
    return lineIntersection((pointsLeft[0], pointsRight[0]), ((x,y0), (x,y1)))
