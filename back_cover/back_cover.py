# -*- coding: utf-8 -*-

import argparse
import calendar
import csv
import inspect
import math
import os
import svgwrite
from svgwrite import inch, px
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.svgutils as svgu
import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
# input source: https://www.ncdc.noaa.gov/monitoring-references/faq/anomalies.php
parser.add_argument('-input', dest="INPUT_FILE", default="data/slr_sla_gbl_free_txj1j2_90.csv", help="Path to input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.25, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/back_cover.svg", help="Path to output file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

rows = []
with open(args.INPUT_FILE, 'rb') as f:
    lines = [line for line in f if not line.startswith("#")]
    reader = csv.DictReader(lines, skipinitialspace=True)
    rows = list(reader)

SLR_KEY_PRIORITY = ["Jason-2", "Jason-1", "TOPEX/Poseidon", "GMSL (mm)"]
values = []
for row in rows:
    for k in SLR_KEY_PRIORITY:
        if k in row and len(row[k]):
            value = float(row[k])
            values.append(value)
count = len(values)
print "Read %s values from %s" % (count, args.INPUT_FILE)

# svg config
COMPRESS_Y = 0.6667
COMPRESS_X = 0.99
LINE_HEIGHT = 30.0
COLOR = "#A92D2D"
COLOR_ALT = "#000000"
ADD_LINE = False

# svg calculations
chartW = WIDTH * COMPRESS_X
chartH = HEIGHT * COMPRESS_Y
offsetY = HEIGHT * (1-COMPRESS_Y) * 0.5
offsetX = WIDTH * (1-COMPRESS_X) * 0.5

# convert values to points
minValue = min(values)
maxValue = max(values)
points = []
for i, v in enumerate(values):
    xp = 1.0 * i / count
    yp = 1.0 - (v - minValue) / (maxValue - minValue)
    x = chartW * xp + PAD + offsetX
    y = chartH * yp + PAD + offsetY
    points.append((x, y))

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# water pattern
waterW = 40
waterH = 98
waterStrokeW = 10
waveHeight = 24
waterPattern = dwg.pattern(id="water", patternUnits="userSpaceOnUse", size=(waterW,waterH))
commands = svgu.patternWater(waterW, waterH, waveHeight)
waterPattern.add(dwg.rect(size=(waterW,waterH), fill=COLOR))
waterPattern.add(dwg.path(d=commands, stroke_width=waterStrokeW, stroke="#FFFFFF", fill="none"))
dwg.defs.add(waterPattern)

# dot pattern
dotSize = 24
dotW = 8
dotPattern = dwg.pattern(id="dot", patternUnits="userSpaceOnUse", size=(dotSize,dotSize))
commands = svgu.patternDiamond(dotSize, dotW)
dotPattern.add(dwg.path(d=commands, fill="#000000"))
dwg.defs.add(dotPattern)

# simplify points
lineOffset = LINE_HEIGHT * 0.5
points = mu.simplify(points, 100)
points = mu.smoothPoints(points, 1, 2.0)
pointsTop = [(p[0], p[1]-lineOffset) for p in points]
pointsBottom = [(p[0], p[1]+lineOffset) for p in points]

# make path commands
x0 = PAD
x1 = WIDTH + PAD
y0 = HEIGHT + PAD
y1 = PAD
p0 = pointsTop[0]
p1 = pointsTop[-1]
cp = 12

# top curve
commandsTop = svgu.pointsToCurve(pointsTop, 0.1)
commandsTop.append("Q%s,%s %s,%s" % (p1[0]+(x1-p1[0])*0.5, p1[1]-cp, x1, p1[1]))
commandsTop.append("L%s,%s" % (x1, y1))
commandsTop.append("L%s,%s" % (x0, y1))
commandsTop.append("L%s,%s" % (x0, p0[1]))
commandsTop.append("Q%s,%s %s,%s" % (x0+(p0[0]-x0)*0.5, p0[1]-cp, p0[0], p0[1]))
dwg.add(dwg.path(d=commandsTop, fill="url(#dot)"))

p0 = pointsBottom[0]
p1 = pointsBottom[-1]

# bottom curve
commandsBottom = svgu.pointsToCurve(pointsBottom, 0.1)
if ADD_LINE:
    line = commandsBottom[:]
    line.insert(0, "Q%s,%s %s,%s" % (x0+(p0[0]-x0)*0.5, p0[1]-cp, p0[0], p0[1]))
    line.insert(0, "M%s,%s" % (x0, p0[1]))
    line.append("Q%s,%s %s,%s" % (p1[0]+(x1-p1[0])*0.5, p1[1]-cp, x1, p1[1]))
    dwg.add(dwg.path(d=line, fill="none", stroke=COLOR, stroke_width=20))
commandsBottom.append("Q%s,%s %s,%s" % (p1[0]+(x1-p1[0])*0.5, p1[1]-cp, x1, p1[1]))
commandsBottom.append("L%s,%s" % (x1, y0))
commandsBottom.append("L%s,%s" % (x0, y0))
commandsBottom.append("L%s,%s" % (x0, p0[1]))
commandsBottom.append("Q%s,%s %s,%s" % (x0+(p0[0]-x0)*0.5, p0[1]-cp, p0[0], p0[1]))
dwg.add(dwg.path(d=commandsBottom, fill="url(#water)"))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
