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

import lib.geojson as geo
import lib.mathutils as mu
import lib.svgutils as svgu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/india.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

print "The total change between 1996 and 2016 is %s million square kilometers" % (7.9-4.7)
print "India's land mass is 3.3 (2.9 land) million square kilometers"

dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# diagonal pattern
diagonalSize = 18
diagonalW = 1
diagonalPattern = dwg.pattern(id="diagonal", patternUnits="userSpaceOnUse", size=(diagonalSize,diagonalSize))
commands = [
    "M0,%s" % diagonalSize,
    "l%s,-%s" % (diagonalSize, diagonalSize),
    "M-%s,%s" % (diagonalSize*0.25, diagonalSize*0.25),
    "l%s,-%s" % (diagonalSize*0.5, diagonalSize*0.5),
    "M%s,%s" % (diagonalSize-diagonalSize*0.25, diagonalSize+diagonalSize*0.25),
    "l%s,-%s" % (diagonalSize*0.5, diagonalSize*0.5)
]
diagonalPattern.add(dwg.rect(size=(diagonalSize,diagonalSize), fill="#ffffff"))
diagonalPattern.add(dwg.path(d=commands, stroke_width=diagonalW, stroke="#000000"))
dwg.defs.add(diagonalPattern)

# get geodata
g = geo.GeoJSONUtil("data/countries.geojson", "ISO_A3", "IND")
# only take the biggest shape
g.onlyBiggestShape()
# determine dimensions
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
    poly = mu.simplify(polygon, 500)
    poly = mu.smoothPoints(poly)
    # poly.append((poly[0][0], poly[0][1]))
    # poly = svgu.pointsToCurve(poly)
    # dwg.add(dwg.path(d=poly, fill="url(#diagonal)", stroke="#000000", stroke_width=2))
    dwg.add(dwg.polygon(points=poly, fill="url(#diagonal)", stroke="#000000", stroke_width=1))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
