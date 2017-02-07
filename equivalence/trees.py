# -*- coding: utf-8 -*-

import inspect
import math
import os
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.svgutils as svgu

# Config
DPI = 72
PAD = 0.5 * DPI
WIDTH = 8.5 * DPI - PAD * 2
HEIGHT = 11 * DPI - PAD * 2
HEADER_H = 1.5 * DPI
COLS = 11
TREES = ['svg/tree01.svg', 'svg/tree02.svg', 'svg/tree03.svg']
OUTPUT_FILE = 'data/trees.svg'
TREE_PLATFORM_H = 0.2 * 72
TREE_PLATFORM_HALF = TREE_PLATFORM_H * 0.5

TREES_H = HEIGHT - HEADER_H

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 0.039 metric ton CO2 per urban tree seedling planted and grown for 10 years
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#seedlings
TREE_SEQUESTERED = 0.039

# Number of tree seedlings grown for 10 years to take one car off the road for a year
trees = int(round(VEHICLE_EMISSIONS / TREE_SEQUESTERED))
print "Taking one car off the road for a year is equivalent to %s urban trees planted and grown for 10 years." % trees

# (Should be 121)

# Retrieve SVG data
treeData = svgu.getDataFromSVGs(TREES)
treeSetCount = len(TREES)
rowCount = int(math.ceil(1.0 * trees / COLS))
treeWidth = 1.0 * WIDTH / (COLS+0.5)
treeHeight = 1.0 * (TREES_H-TREE_PLATFORM_H) / rowCount
halfWidth = treeWidth * 0.5
halfHeight = treeHeight * 0.5

# Add more tree data
for i, tree in enumerate(treeData):
    treeData[i]["id"] = "tree%s" % i
    scale = treeWidth / tree["width"]
    treeData[i]["scale"] = scale
    treeData[i]["sWidth"] = tree["width"] * scale
    treeData[i]["sHeight"] = tree["height"] * scale

# Init SVG
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# Add tree definitions
for i, tree in enumerate(treeData):
    dwgTree = dwg.g(id=tree["id"])
    strokeWidth = 1.3 / tree["scale"]
    for path in tree["paths"]:
        dwgTree.add(dwg.path(d=path, stroke_width=strokeWidth, stroke="#000000", fill="#FFFFFF"))
    dwg.defs.add(dwgTree)

dwgTrees = dwg.g(id="trees")
# degRectInner = dwg.g(id="rects_inner")
degRectOuter = dwg.g(id="rects_outer")
for row in range(rowCount):
    offsetX = PAD
    offsetY = PAD + HEADER_H
    if row % 2 > 0:
        offsetX += halfWidth
    for col in range(COLS):
        count = row * COLS + col
        x = col * treeWidth + offsetX
        y = row * treeHeight + offsetY - (tree["sHeight"] - treeHeight)
        cx = x + halfWidth
        cy = y + halfHeight

        treeSet = count % treeSetCount
        tree = treeData[treeSet]

        t = "translate(%s, %s) scale(%s)" % (x, y, tree["scale"])
        dwgTree = dwg.g(transform=t)
        dwgTree.add(dwg.use("#"+tree["id"]))
        dwgTrees.add(dwgTree)

        ph = TREE_PLATFORM_H
        py = y + tree["sHeight"]
        points = [(cx,py-ph), (x,py), (cx,py+ph), (x+treeWidth,py)]
        dwgRect = dwg.polygon(points=points, stroke_width=1, stroke="#000000", fill="#FFFFFF")
        degRectOuter.add(dwgRect)

        if count >= trees-1:
            break

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.add(degRectOuter)
# dwg.add(degRectInner)
dwg.add(dwgTrees)
dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
