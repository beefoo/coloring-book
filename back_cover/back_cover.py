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

import lib.geojson as geo
import lib.mathutils as mu
import lib.svgutils as svgu


# input
parser = argparse.ArgumentParser()
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
COLOR = "#A92D2D"

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# water pattern
waterW = 24
waterH = 60
waterStrokeW = 4
waveHeight = 14
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
dwg.add(dwg.rect(insert=(PAD, PAD), size=(WIDTH, HEIGHT), fill="url(#dot)"))

data = svgu.getDataFromSVG("../sea_ice/data/extent_N_polygon_v2.svg")
paths = [path for path in data["paths"] if len(path) > 200]
for i, path in enumerate(paths):
    fill = "#FFFFFF"
    if i <= 0:
        fill = "url(#water)"
    dwg.add(dwg.path(d=path, fill=fill))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
