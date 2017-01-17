# -*- coding: utf-8 -*-

import math
from shared import getDataFromSVGs
from shared import getTransformString
import svgwrite

# Config
WIDTH = 1000
PAD = 200
TREES = ['svg/pine02.svg']
OUTPUT_FILE = 'data/forests.svg'
TREES_CENTER_ROW = 5

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 1.06 metric ton CO2 sequestered annually by one acre of average U.S. forest.
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#pineforests
ACRE_FOREST_SEQUESTERED = 1.06

# Acres of U.S. forests to take one car off the road for a year
forests = int(round(VEHICLE_EMISSIONS / ACRE_FOREST_SEQUESTERED))
print "%s acres of forest necessary." % forests

# Retrieve SVG data
treeData = getDataFromSVGs(TREES)
treeSetCount = len(TREES)
forestWidth = WIDTH * 0.5
forestHeight = forestWidth
halfWidth = forestWidth * 0.5
halfHeight = forestHeight * 0.5

# Add more tree data
for i, tree in enumerate(treeData):
    treeData[i]["id"] = "tree%s" % i
    treeData[i]["scale"] = 1

# Init SVG
height = WIDTH
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(WIDTH+PAD*2, height+PAD*2), profile='full')

# Add tree definitions
for i, tree in enumerate(treeData):
    dwgTree = dwg.g(id=tree["id"])
    for path in tree["paths"]:
        dwgTree.add(dwg.path(d=path, stroke_width=1, stroke="#000000", fill="#FFFFFF"))
    dwg.defs.add(dwgTree)

dwgTrees = dwg.g(id="trees")
dwgRects = dwg.g(id="rects")

def addRect(w, h, x, y, sx, sy, r):
    global dwg
    global dwgRects
    t = getTransformString(w, h, x, y, sx, sy, r)
    dwgRect = dwg.rect(size=(w, h), stroke_width=2, stroke="#000000", fill="#FFFFFF")
    dwgRectWrapper = dwg.g(transform=t)
    dwgRectWrapper.add(dwgRect)
    dwgRects.add(dwgRectWrapper)

treeIndex = 0
def addTree(w, cx, cy):
    global treeIndex
    global dwg
    global dwgTrees

    # dwgTrees.add(dwg.circle(center=(cx, cy), r=10, fill="black"))
    tree = treeData[treeIndex % treeSetCount]
    scale = w / tree["width"]
    x = cx - tree["width"] * 0.5
    y = cy - tree["height"] * 0.5 - tree["height"] * scale * 0.5
    t = getTransformString(tree["width"], tree["height"], x, y, scale, scale)

    dwgTree = dwg.g(transform=t)
    dwgTree.add(dwg.use("#"+tree["id"]))
    dwgTrees.add(dwgTree)

    treeIndex += 1

# (Should be 4)
x = 0
y = 0
sx = 0.6667
sy = 0.3
dx = math.sqrt(2.0 * math.pow(forestWidth * sx, 2)) * 0.5
dy = math.sqrt(2.0 * math.pow(forestHeight * sy, 2)) * 0.5
offsetX = forestWidth*0.2
for forest in range(forests):
    # determine x
    x = -offsetX
    if forest % 3 == 0:
        x = halfWidth
    elif forest % 3 == 2:
        x = forestWidth + offsetX

    # add rectangle
    addRect(forestWidth, forestHeight, x+PAD, y+PAD, sx*1.2, sy*1.2, 45)
    addRect(forestWidth, forestHeight, x+PAD, y+PAD, sx, sy, 45)

    # add trees
    cx = x + halfWidth + PAD
    cy = y + halfHeight + PAD
    rows = (TREES_CENTER_ROW - 1) * 2 + 1
    cols = 1
    tpad = 0.8
    dty = dy / (TREES_CENTER_ROW - 1) * tpad
    dtx = dx * 2 / (TREES_CENTER_ROW - 1) * tpad
    _y = cy - (TREES_CENTER_ROW - 1) * dty
    for row in range(rows):
        _x = cx - (cols - 1) * dtx * 0.5
        for col in range(cols):
            addTree(dtx, _x, _y)
            _x += dtx
        _y += dty
        if row < TREES_CENTER_ROW-1:
            cols += 1
        else:
            cols -= 1

    # increment y
    if forest % 3 in [0, 2]:
        y += halfHeight * sx

dwg.add(dwgRects)
dwg.add(dwgTrees)
dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
