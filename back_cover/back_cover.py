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
parser.add_argument('-input', dest="INPUT_FILE", default="../sea_ice/data/extent_N_199609_polygon_v2/extent_N_199609_polygon_v2", help="Path to input shapefiles")
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
waterW = 36
waterH = 72
waterStrokeW = 2
waveHeight = 18
waterPattern = dwg.pattern(id="water", patternUnits="userSpaceOnUse", size=(waterW,waterH))
commands = svgu.patternWater(waterW, waterH, waveHeight)
waterPattern.add(dwg.path(d=commands, stroke_width=waterStrokeW, stroke="#000000", fill="none"))
dwg.defs.add(waterPattern)
dwg.add(dwg.rect(insert=(PAD, PAD), size=(WIDTH, HEIGHT), fill="url(#water)"))

# diagonal pattern
diagonalSize = 48
diagonalW = 12
diagonalPattern = dwg.pattern(id="diagonal", patternUnits="userSpaceOnUse", size=(diagonalSize,diagonalSize))
commands = svgu.patternDiagonal(diagonalSize, "down")
diagonalPattern.add(dwg.rect(size=(diagonalSize,diagonalSize), fill="#FFFFFF"))
diagonalPattern.add(dwg.path(d=commands, stroke_width=diagonalW, stroke=COLOR))
dwg.defs.add(diagonalPattern)

# get geojson data
g = geo.GeoJSONUtil(args.INPUT_FILE)
g.onlyBiggestShape()
(w, h) = g.getDimensions()
offsetX = 0
offsetY = 0
width = WIDTH
height = width * (1.0 * h / w)
if height > HEIGHT:
    width = HEIGHT * (1.0 * w / h)
    height = HEIGHT
    offsetX = (WIDTH - width) * 0.5
else:
    offsetY = (HEIGHT - height) * 0.5
polygons = g.toPolygons(WIDTH, PAD+offsetX, PAD+offsetY)
# polygons
for polygon in polygons:
    poly = mu.smoothPoints(polygon)
    poly.append((poly[0][0], poly[0][1]))
    poly = svgu.pointsToCurve(poly)
    dwg.add(dwg.path(d=poly, fill="url(#diagonal)", stroke="#FFFFFF", stroke_width=4))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
