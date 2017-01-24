# -*- coding: utf-8 -*-

import math

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

# convert points to curve
def pointsToCurve(points, control_point_delta=0.3):
    commands = []
    for i, point in enumerate(points):
        # first point: move to point
        if i <= 0:
            commands.append("M%s,%s" % point)
        else:
            # get previous and next point
            p0 = points[i-1]
            d = distance(p0, point)
            cpd = d * control_point_delta
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
