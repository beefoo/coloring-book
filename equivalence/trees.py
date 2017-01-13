# -*- coding: utf-8 -*-

import math
from shared import getDataFromSVGs
import svgwrite

# Config
WIDTH = 1000
COLS = 11
PAD = 100
TREES = ['svg/tree01.svg', 'svg/tree02.svg', 'svg/tree03.svg']
OUTPUT_FILE = 'data/trees.svg'

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 0.039 metric ton CO2 per urban tree seedling planted and grown for 10 years
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#seedlings
TREE_SEQUESTERED = 0.039

# Number of tree seedlings grown for 10 years to take one car off the road for a year
trees = int(round(VEHICLE_EMISSIONS / TREE_SEQUESTERED))
print "%s trees necessary." % trees

# (Should be 121)

# Retrieve SVG data
treeData = getDataFromSVGs(TREES)
treeSetCount = len(TREES)
rowCount = int(math.ceil(1.0 * trees / COLS))
treeWidth = 1.0 * WIDTH / COLS
treeHeight = treeWidth
halfWidth = treeWidth * 0.5
halfHeight = treeHeight * 0.5

# Add more tree data
for i, tree in enumerate(treeData):
    treeData[i]["id"] = "tree%s" % i
    treeData[i]["scale"] = treeWidth / tree["width"]

# Init SVG
height = WIDTH
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(WIDTH+PAD*2+halfWidth, height+PAD*2), profile='full')

# Add tree definitions
for i, tree in enumerate(treeData):
    dwgTree = dwg.g(id=tree["id"])
    for path in tree["paths"]:
        dwgTree.add(dwg.path(d=path, stroke_width=1, stroke="#000000", fill="#FFFFFF"))
    dwg.defs.add(dwgTree)

dwgTrees = dwg.g(id="trees")
degRectInner = dwg.g(id="rects_inner")
degRectOuter = dwg.g(id="rects_outer")
for row in range(rowCount):
    offsetX = 0
    if row % 2 > 0:
        offsetX = halfWidth
    for col in range(COLS):
        count = row * COLS + col
        x = col * treeWidth + PAD + offsetX
        y = row * treeHeight + PAD
        cx = x + halfWidth
        cy = y + halfHeight

        treeSet = count % treeSetCount
        tree = treeData[treeSet]

        t = "translate(%s,%s) scale(%s)" % (x-halfWidth*(tree["scale"]-1), y-halfHeight*(tree["scale"]-1), tree["scale"])
        dwgTree = dwg.g(transform=t)
        dwgTree.add(dwg.use("#"+tree["id"]))
        dwgTrees.add(dwgTree)

        rectScaleX = 0.7
        rectScaleY = 0.4
        rectTransX = x-halfWidth*(rectScaleX-1) + treeWidth * 0.05
        rectTransY = y-halfHeight*(rectScaleY-1) + treeHeight * 0.8
        t = "translate(%s,%s) scale(%s, %s) rotate(45, %s, %s)" % (rectTransX, rectTransY, rectScaleX, rectScaleY, halfWidth, halfHeight)
        dwgRect = dwg.rect(size=(treeWidth, treeWidth), stroke_width=2, stroke="#000000", fill="#FFFFFF")
        dwgRectWrapper = dwg.g(transform=t)
        dwgRectWrapper.add(dwgRect)
        degRectOuter.add(dwgRectWrapper)

        rectScaleX *= 0.75
        rectScaleY *= 0.75
        rectTransX = x-halfWidth*(rectScaleX-1) + treeWidth * 0.05
        rectTransY = y-halfHeight*(rectScaleY-1) + treeHeight * 0.8
        t = "translate(%s,%s) scale(%s, %s) rotate(45, %s, %s)" % (rectTransX, rectTransY, rectScaleX, rectScaleY, halfWidth, halfHeight)
        dwgRect = dwg.rect(size=(treeWidth, treeWidth), stroke_width=2, stroke="#000000", fill="#FFFFFF")
        dwgRectWrapper = dwg.g(transform=t)
        dwgRectWrapper.add(dwgRect)
        degRectInner.add(dwgRectWrapper)

        if count >= trees-1:
            break

dwg.add(degRectOuter)
dwg.add(degRectInner)
dwg.add(dwgTrees)
dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
