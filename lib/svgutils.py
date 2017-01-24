# -*- coding: utf-8 -*-

import math
import re

# Utility functions

def angleBetweenPoints(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    deltaX = x2 - x1
    deltaY = y2 - y1
    return math.atan2(deltaY, deltaX) * 180.0 / math.pi

def flattenTuples(tuples):
    return tuple([i for sub in tuples for i in sub])

def distance(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return math.hypot(x2 - x1, y2 - y1)

def translatePoint(p, angle, distance):
    (x, y) = p
    r = math.radians(angle)
    x2 = x + distance * math.cos(r)
    y2 = y + distance * math.sin(r)
    return (x2, y2)

# SVG file functions

def getDataFromSVG(filename):
    paths = []
    polygons = []
    width = 0
    height = 0
    with open(filename, 'rb') as f:
        contents = f.read().replace('\n', '')
        # find dimensions
        match = re.search(r'viewBox="0 0 ([0-9\.]+) ([0-9\.]+)"', contents)
        if match:
            width = float(match.group(1))
            height = float(match.group(2))
        else:
            print "Warning: could not find dimensions for %s" % filename

        # find the path data
        matches = re.findall(r'\sd="([^"]+)"\s', contents)
        if matches and len(matches):
            paths = list(matches)
        else:
            print "Warning: couldn't find paths in %s" % filename

        # find the polygon data
        matches = re.findall(r'\spoints="([^"]+)"\s', contents)
        if matches and len(matches):
            polygons = list(matches)

    # return data
    return {
        "width": width,
        "height": height,
        "paths": paths,
        "polygons": polygons
    }

def getDataFromSVGs(filenames):
    data = []
    for filename in filenames:
        fileData = getDataFromSVG(filename)
        data.append(fileData)
    return data

# SVG parameter functions

def getTransformString(w, h, x, y, sx=1, sy=1, r=0):
    hw = w * 0.5
    hh = h * 0.5
    tx = x - hw * (sx-1)
    ty = y - hh * (sy-1)
    transform = "translate(%s,%s) scale(%s, %s) rotate(%s, %s, %s)" % (tx, ty, sx, sy, r, hw, hh)
    if r==0:
        transform = "translate(%s,%s) scale(%s, %s)" % (tx, ty, sx, sy)
    return transform

# convert points to curve
# recommended curviness range: 0.1 - 0.5
def pointsToCurve(points, curviness=0.3):
    commands = []
    for i, point in enumerate(points):
        # first point: move to point
        if i <= 0:
            commands.append("M%s,%s" % point)
        else:
            # get previous and next point
            p0 = points[i-1]
            d = distance(p0, point)
            cpd = d * curviness
            p2 = None
            if i < len(points)-1:
                p2 = points[i+1]
            # draw a straight line from previous to next
            if p2:
                a2 = angleBetweenPoints(p2, p0)
                cp2 = translatePoint(point, a2, cpd)
                # second point: curve to
                if i <= 1:
                    a0 = angleBetweenPoints(p0, point)
                    cp0 = translatePoint(p0, a0, cpd)
                    commands.append("C%s,%s %s,%s %s,%s" % flattenTuples([cp0, cp2, point]))
                # otherwise, shorthand curve to
                else:
                    commands.append("S%s,%s %s,%s" % flattenTuples([cp2, point]))
            # last point
            else:
                a2 = angleBetweenPoints(point, p0)
                cp2 = translatePoint(point, a2, cpd)
                commands.append("S%s,%s %s,%s" % flattenTuples([cp2, point]))
    return commands
