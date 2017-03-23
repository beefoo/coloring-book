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
SPIRAL_A = 8.8
CORAL_R = 10

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

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgCorals = dwg.add(dwg.g(id="corals"))
dwgLabels = dwg.add(dwg.g(id="labels"))
dwgLabelGroups = {}
for g in SURVEY_DATA:
    dwgLabelGroups[g["display"]] = dwgLabels.add(dwg.g(id="labels%s" % g["display"]))

# draw corals
for coral in corals:
    dwgCorals.add(dwg.circle(center=coral["point"], r=CORAL_R, stroke="#000000", stroke_width=1, fill="#ffffff"))
    dwgLabelGroups[coral["label"]].add(dwg.text(coral["label"], insert=coral["point"], text_anchor="middle", alignment_baseline="middle", font_size=11))

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
