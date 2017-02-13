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

def polarToCartesian(cx, cy, rx, ry, degrees):
    radians = math.radians(degrees)
    return (
        cx + (rx * math.cos(radians)),
        cy + (ry * math.sin(radians))
    )

def translatePoint(p, angle, distance):
    (x, y) = p
    r = math.radians(angle)
    x2 = x + distance * math.cos(r)
    y2 = y + distance * math.sin(r)
    return (x2, y2)

# SVG file functions

def describeArc(x, y, rx, ry, startAngle, endAngle):
    start = polarToCartesian(x, y, rx, ry, endAngle)
    end = polarToCartesian(x, y, rx, ry, startAngle)
    largeArcFlag = 0
    if (endAngle - startAngle) > 180:
        largeArcFlag = 1
    sweepFlag = 0
    if startAngle > endAngle:
        sweepFlag = 1
    d = [
        "M%s,%s" % start,
        "A%s,%s,%s,%s,%s,%s,%s" % (rx, ry, 0, largeArcFlag, sweepFlag, end[0], end[1])
    ]
    return d

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
        matches = re.findall(r'\sd="([^"]+)"[\s\/]', contents)
        if matches and len(matches):
            paths = list(matches)
        else:
            print "Warning: couldn't find paths in %s" % filename

        # find the polygon data
        matches = re.findall(r'\spoints="([^"]+)"[\s\/]', contents)
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

def patternDiagonal(size, direction="up"):
    commands = [
        "M0,%s" % size,
        "l%s,-%s" % (size, size),
        "M-%s,%s" % (size*0.25, size*0.25),
        "l%s,-%s" % (size*0.5, size*0.5),
        "M%s,%s" % (size*0.75, size*1.25),
        "l%s,-%s" % (size*0.5, size*0.5)
    ]
    if direction=="down":
        commands = [
            "M0,0",
            "l%s,%s" % (size, size),
            "M-%s,%s" % (size*0.25, size*0.75),
            "l%s,%s" % (size*0.5, size*0.5),
            "M%s,-%s" % (size*0.75, size*0.25),
            "l%s,%s" % (size*0.5, size*0.5)
        ]
    return commands

def patternDiamond(size=24, dotSize=8):
    dotR = dotSize / 2
    dotC = size / 2
    commands = [
        "M0,0",
        "L%s,%s" % (0, dotR),
        "L%s,%s" % (dotR, 0),
        "Z",
        "M%s,%s" % (size, 0),
        "L%s,%s" % (size, dotR),
        "L%s,%s" % (size-dotR, 0),
        "Z",
        "M%s,%s" % (0, size),
        "L%s,%s" % (dotR, size),
        "L%s,%s" % (0, size-dotR),
        "Z",
        "M%s,%s" % (size, size),
        "L%s,%s" % (size-dotR, size),
        "L%s,%s" % (size, size-dotR),
        "Z",
        "M%s,%s" % (dotC, dotC-dotR),
        "L%s,%s" % (dotC-dotR, dotC),
        "L%s,%s" % (dotC, dotC+dotR),
        "L%s,%s" % (dotC+dotR, dotC),
        "Z"
    ]
    return commands

def patternWater(width=24, height=36, waveHeight=12):
    w = width
    h = height
    wh = waveHeight
    hw = width * 0.5
    offsetH = (h - wh * 2) * 0.5
    hh = h - offsetH
    commands = [
        "M%s,%s" % (0,0),
        "C%s,%s %s,%s %s,%s" % (0, wh, w, wh, w, 0),
        "M-%s,%s" % (hw, hh-wh),
        "C-%s,%s %s,%s %s,%s" % (hw, hh, hw, hh, hw, hh-wh),
        "M%s,%s" % (hw, hh-wh),
        "C%s,%s %s,%s %s,%s" % (hw, hh, w+hw, hh, w+hw, hh-wh)
    ]
    return commands

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
