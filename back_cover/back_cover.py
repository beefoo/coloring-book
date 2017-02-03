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

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# water pattern
waterW = 36
waterH = 72
waterStrokeW = 2
waveHeight = 18
waterPattern = dwg.pattern(id="water", patternUnits="userSpaceOnUse", size=(waterW,waterH))
commands = svgu.patternWater(waterW, waterH, waveHeight)
waterPattern.add(dwg.path(d=commands, stroke_width=waterStrokeW, stroke="#000000", fill="none"))
dwg.defs.add(waterPattern)

dwg.add(dwg.rect(insert=(PAD, PAD), size=(WIDTH, HEIGHT), fill="url(#water)"))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
