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

import lib.mathutils as mu

# Config
DPI = 72
PAD = 0.5 * DPI
WIDTH = 8.5 * DPI - PAD * 2
HEIGHT = 11 * DPI - PAD * 2
TREES = ['svg/pine02.svg']
OUTPUT_FILE = 'data/forests.svg'
ACRES_PER_ROW = 2
ACRE_PAD = 0.2 * DPI
TREES_PER_ROW = 4
TREE_HEIGHT = 2.0 * DPI
TREE_WIDTH = 0.625 * DPI
STUMP_HEIGHT = TREE_HEIGHT * 0.1
STUMP_WIDTH =  TREE_WIDTH * 0.2
ACRE_HEIGHT_RATIO = 0.825
MARGIN_X = 0 * DPI
MARGIN_Y = 0.5 * DPI

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 1.06 metric ton CO2 sequestered annually by one acre of average U.S. forest.
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#pineforests
ACRE_FOREST_SEQUESTERED = 1.06

# Acres of U.S. forests to take one car off the road for a year
forests = int(round(VEHICLE_EMISSIONS / ACRE_FOREST_SEQUESTERED))
print "Taking one car off the road for a year is equivalent to %s acres of North American pine forest." % forests
# Should be 4

# Calculations
rows = int(math.ceil(1.0 * forests / ACRES_PER_ROW))
acreWidth = 1.0 * (WIDTH - MARGIN_X * (ACRES_PER_ROW - 1) - (TREE_WIDTH-ACRE_PAD*2) * ACRES_PER_ROW) / ACRES_PER_ROW
acreHeight = acreWidth * ACRE_HEIGHT_RATIO
height = acreHeight * rows + MARGIN_Y * (rows-1)

# Init SVG
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

# Tree ref
halfTree = TREE_WIDTH * 0.5
halfStump = STUMP_WIDTH * 0.5
stumpY = TREE_HEIGHT - STUMP_HEIGHT
tree = [
    (halfTree, 0),
    (0, stumpY),
    (halfTree-halfStump, stumpY),
    (halfTree-halfStump, TREE_HEIGHT),
    (halfTree+halfStump, TREE_HEIGHT),
    (halfTree+halfStump, stumpY),
    (TREE_WIDTH, stumpY),
    (halfTree, 0)
]
dwgTree = dwg.polygon(id="tree", points=tree, stroke_width=1.5, stroke="#000000", fill="#FFFFFF")
dwg.defs.add(dwgTree)

# Draw forests
xOffset = PAD + TREE_WIDTH * 0.5 - ACRE_PAD
yOffset = HEIGHT + PAD - height
for row in range(rows):
    x = xOffset
    y = yOffset
    for col in range(ACRES_PER_ROW):
        i = row * ACRES_PER_ROW + col
        xc = x + acreWidth * 0.5
        x1 = x + acreWidth
        yc = y + acreHeight * 0.5
        y1 = y + acreHeight
        # Draw rect
        points = [(x,yc), (xc,y), (x1,yc), (xc,y1)]
        dwgGroup = dwg.add(dwg.g(id="acre%s" % i))
        dwgGroup.add(dwg.polygon(points=points, stroke_width=2, stroke="#000000", fill="none"))
        # Draw trees
        tp = ACRE_PAD
        tbox = [(x+tp,yc), (xc,y+tp), (x1-tp,yc), (xc,y1-tp)]
        tps = []
        for trow in range(TREES_PER_ROW):
            a = mu.lerp2D(tbox[0], tbox[3], 1.0*trow/(TREES_PER_ROW-1))
            b = mu.lerp2D(tbox[1], tbox[2], 1.0*trow/(TREES_PER_ROW-1))
            for tcol in range(TREES_PER_ROW):
                p = mu.lerp2D(a, b, 1.0*tcol/(TREES_PER_ROW-1))
                tp = (p[0]-halfTree, p[1]-TREE_HEIGHT)
                tps.append(tp)
        # sort based on y unit
        tps = sorted(tps, key=lambda p: p[1])
        for tp in tps:
            dwgGroup.add(dwg.use("#tree", insert=tp))
        x += MARGIN_X + acreWidth + TREE_WIDTH - ACRE_PAD * 2
    yOffset += MARGIN_Y + acreHeight

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
