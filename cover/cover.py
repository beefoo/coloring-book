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

# input
parser = argparse.ArgumentParser()
# input source: https://www.ncdc.noaa.gov/monitoring-references/faq/anomalies.php
parser.add_argument('-input', dest="INPUT_FILE", default="data/1880-2016_land_ocean.csv", help="Path to input file")
parser.add_argument('-y0', dest="YEAR_START", type=int, default=1880, help="Year start on viz")
parser.add_argument('-ys', dest="YEAR_STEP", type=int, default=1, help="Year step on viz")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.25, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/cover.svg", help="Path to output file")

# init input
args = parser.parse_args()
DPI = 150
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
YEAR_START = args.YEAR_START
YEAR_STEP = args.YEAR_STEP
INVERT = False
BOTTOM_PAD = 0.333

bottomH = HEIGHT * BOTTOM_PAD
topH = HEIGHT - bottomH
values = []

# read csv
with open(args.INPUT_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    for skip in range(4):
        next(r, None)
    # for each row
    i = 0
    for _year,_value in r:
        year = int(_year)
        if i % YEAR_STEP <= 0 and year >= YEAR_START:
            value = float(_value)
            values.append(value)
        if year >= YEAR_START:
            i += 1
count = len(values)
print "Read %s values from %s" % (count, args.INPUT_FILE)

# convert values to points
minValue = min(values)
maxValue = max(values)
points = []
for i, v in enumerate(values):
    xp = 1.0 * i / count
    yp = 1.0 - (v - minValue) / (maxValue - minValue)
    x = WIDTH * xp + PAD
    y = topH * yp + PAD
    points.append((x, y))

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# make path commands
commands = svgu.pointsToCurve(points, 0.1)
if INVERT:
    commands.append("L%s,%s" % (WIDTH + PAD, PAD))
    commands.append("L%s,%s" % (PAD, PAD))
    commands.append("L%s,%s" % points[0])
else:
    commands.append("L%s,%s" % (WIDTH + PAD, HEIGHT + PAD))
    commands.append("L%s,%s" % (PAD, HEIGHT + PAD))
    commands.append("L%s,%s" % points[0])
dwg.add(dwg.path(d=commands))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
