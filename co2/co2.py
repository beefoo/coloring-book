# -*- coding: utf-8 -*-

import argparse
import inspect
import math
import os
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
# Source: http://cdiac.ornl.gov/trends/emis/tre_glob_2014.html
# Unit: One million metric tons of carbon
parser.add_argument('-in', dest="INPUT_FILE", default="data/global.1751_2014.csv", help="Input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-rad', dest="RADIUS", type=float, default=5, help="Radius")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/co2.svg", help="Path to output svg file")

args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
RADIUS = args.RADIUS

LABEL_H = 28
MARGIN = 20
ROWS = 2
COLS = 2

CONFIG = [
    {"year": "1760", "label": "1760 (Industrial Revolution begins)", "width": 0.5, "height": 0.33, "top": 0, "left": 0, "row": 0, "col": 0},
    {"year": "1870", "label": "1870 (Second Industrial Revolution begins)", "width": 0.5, "height": 0.33, "top": 0, "left": 0.5, "row": 0, "col": 1},
    {"year": "2014", "label": "2014 (Latest measurement)", "width": 1.0, "height": 0.67, "top": 0.33, "left": 0, "row": 1, "col": 0}
]

# Retrieve data
data = {}
with open(args.INPUT_FILE) as f:
    lines = f.readlines()
    # skip header and notes
    lines.pop(0)
    lines.pop(0)
    for line in lines:
        cols = line.split(",")
        data[cols[0]] = int(cols[1])

# Calculations
availableW = WIDTH - (COLS-1) * MARGIN
availableH = HEIGHT

dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgLabels = dwg.add(dwg.g(id="labels"))
dwg.defs.add(dwg.circle(id="circle", center=(0, 0), r=RADIUS, fill="#FFFFFF", stroke="#000000", stroke_width=1))

for entry in CONFIG:
    group = dwg.add(dwg.g(id="year%s" % entry["year"]))

    # get group size
    gw = entry["width"] * availableW
    gh = entry["height"] * availableH - LABEL_H
    if entry["width"] >= 1.0:
        gw = WIDTH

    # get positions
    ty = PAD + entry["top"] * availableH + LABEL_H * 0.5
    gx = PAD + entry["left"] * availableW + entry["col"] * MARGIN
    tx = gx + gw * 0.5
    gy = ty + LABEL_H * 0.5

    # draw label
    dwgLabels.add(dwg.text(entry["label"], insert=(tx, ty), text_anchor="middle", alignment_baseline="middle", font_size=13))

    # draw rectangle
    group.add(dwg.rect(insert=(gx, gy), size=(gw, gh), fill="none", stroke="#000000", stroke_width=2))

    # draw circles
    value = data[entry["year"]]
    for index in range(value):
        hx = mu.halton(index+1, 3)
        hy = mu.halton(index+1, 5)
        cx = hx * (gw - RADIUS*2) + gx + RADIUS
        cy = hy * (gh - RADIUS*2) + gy + RADIUS
        group.add(dwg.use("#circle", insert=(cx, cy)))

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
