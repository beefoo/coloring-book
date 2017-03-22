# -*- coding: utf-8 -*-

import argparse
import inspect
import math
import os
from pprint import pprint
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.mathutils as mu

# Source:
# Interim report: 2016 coral bleaching event on the Great Barrier Reef
# http://elibrary.gbrmpa.gov.au/jspui/handle/11017/3044
# Great Barrier Reef Marine Park Authority, Australian Government

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11.0, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/coral.svg", help="Path to output svg file")

args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

# config design
SPIRAL_A = 9
MAX_DIST_BETWEEN = 20
MAX_CONNECTIONS_AHEAD = 2
MAX_CONNECTIONS_BEHIND = 1
CORAL_THICKNESS = 10

# config data
SURVEY_COUNT = 873
SURVEY_DATA = [
    {"display": "0", "label": "No bleaching", "count": int(round(0.079*SURVEY_COUNT))},
    {"display": "1", "label": "Minor bleaching", "count": int(round(0.486*SURVEY_COUNT))},
    {"display": "2", "label": "Moderate bleaching", "count": int(round(0.103*SURVEY_COUNT))},
    {"display": "3", "label": "Severe bleaching", "count": int(round(0.332*SURVEY_COUNT))}
]
# print "%s = %s" % (SURVEY_COUNT, sum([d["count"] for d in SURVEY_DATA]))

# Create labels
labels = []
for l in SURVEY_DATA:
    labels += [l["display"] for i in range(l["count"])]

corals = []
cx = PAD + WIDTH * 0.5
cy = PAD + HEIGHT * 0.5
center = (cx, cy)
a = SPIRAL_A
angle = 2.39983333 # golden ratio
for i in range(SURVEY_COUNT):
    x = a * math.sqrt(i+1) * math.cos((i+1) * angle) + cx
    y = a * math.sqrt(i+1) * math.sin((i+1) * angle) + cy
    corals.append({
        "point": (x,y),
        "angle": mu.radiansBetweenPoints(center, (x,y)),
        "distance": mu.distanceBetweenPoints(center, (x,y)),
        "ahead": [],
        "behind": []
    })

# sort by angle
corals = sorted(corals, key=lambda c: c["angle"])

# add labels
for i,c in enumerate(corals):
    corals[i]["label"] = labels[i]

# group by labels
groups = []
for l in SURVEY_DATA:
    coralGroup = [c for c in corals if c["label"]==l["display"]]
    # coralGroup = sorted(coralGroup, key=lambda c: c["distance"])
    # add index
    for i, c in enumerate(coralGroup):
        coralGroup[i]["index"] = i
    groups.append(coralGroup)

# determine neighbors
for i, group in enumerate(groups):

    for j, coral in enumerate(group):

        # retrieve the two closest corals
        closestAhead = [dict(c, **{"distbtwn": mu.distanceBetweenPoints(c["point"], coral["point"])}) for c in group if c["distance"] > coral["distance"]]
        # remove anything that is too far away
        closestAhead = [c for c in closestAhead if c["distbtwn"] <= MAX_DIST_BETWEEN]
        # choose two closest
        closestAhead = sorted(closestAhead, key=lambda c: c["distbtwn"])
        closestAhead = closestAhead[:MAX_CONNECTIONS_AHEAD]
        for a in closestAhead:
            # if coral has no connection behind it, make the connection
            if len(a["behind"]) < MAX_CONNECTIONS_BEHIND:
                groups[i][j]["ahead"].append(a.copy())
                groups[i][a["index"]]["behind"].append(coral.copy())

# add connections for coral with no neighbors
for i, group in enumerate(groups):
    for j, coral in enumerate(group):
        if len(coral["ahead"]) <= 0 and len(coral["behind"]) <= 0:
            others = [dict(c, **{"distbtwn": mu.distanceBetweenPoints(c["point"], coral["point"])}) for c in group if c["index"] != coral["index"]]
            othersByDistance = sorted(others, key=lambda c: c["distbtwn"])
            closest = othersByDistance[0]
            groups[i][j]["ahead"].append(closest.copy())

def getBase(point, angle, width, rtl=False):
    t = width
    ht = width * 0.5
    p = point
    a = angle
    r = math.radians(a)
    rP1 = math.radians(a - 90.0)
    rP2 = math.radians(a + 90.0)
    rR = math.radians(a + 180.0)

    basePoint = mu.translatePoint(p, rR, ht)
    p1 = mu.translatePoint(basePoint, rP1, ht)
    p2 = mu.translatePoint(basePoint, rP2, ht)
    base = [p1, p2]
    if rtl:
        base = [p2, p1]
    return base

# add paths
for i, group in enumerate(groups):
    for j, coral in enumerate(group):
        p = coral["point"]
        a = coral["angle"]
        neighbors = coral["ahead"]
        path = getBase(p, a, CORAL_THICKNESS)

        # only one neighbor ahead
        if len(neighbors) == 1:
            path += getBase(neighbors[0]["point"], neighbors[0]["angle"], CORAL_THICKNESS, True)

        # two neighbors ahead
        elif len(neighbors) == 2:

            # make sure we get the point that is closest to the last point on the path
            neighbors = [dict(c, **{"distbtwn": mu.distanceBetweenPoints(c["point"], path[1])}) for c in neighbors]
            neighbors = sorted(neighbors, key=lambda c: c["distbtwn"])

            # add the first neighbor
            path += getBase(neighbors[0]["point"], neighbors[0]["angle"], CORAL_THICKNESS, True)

            # add mid-point
            path += [mu.translatePoint(p, a, CORAL_THICKNESS * 0.5)]

            # add last neighbor
            path += getBase(neighbors[1]["point"], neighbors[1]["angle"], CORAL_THICKNESS, True)

        # no neighbors ahead
        else:
            target = mu.translatePoint(p, math.radians(a), CORAL_THICKNESS * 2)
            path += getBase(target, a, CORAL_THICKNESS, True)

        # close the path
        path += [path[0]]
        groups[i][j]["path"] = path

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgCorals = dwg.add(dwg.g(id="corals"))
dwgLabels = dwg.add(dwg.g(id="labels"))

# draw corals
for group in groups:
    for coral in group:
        # dwgCorals.add(dwg.polygon(points=coral["path"], stroke="#000000", stroke_width=1, fill="none"))
        for n in coral["ahead"]:
            dwgCorals.add(dwg.line(start=coral["point"], end=n["point"], stroke="#000000", stroke_width=1))
        dwgLabels.add(dwg.text(coral["label"], insert=coral["point"], text_anchor="middle", alignment_baseline="middle", font_size=11))

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
