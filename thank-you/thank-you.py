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
WIDTH = 7.5 * DPI
HEIGHT = 7.5 * DPI
OUTPUT_FILE = 'thank-you.svg'
INPUT_FILE = 'badge.svg'
COUNT = 829
COLS = 26
ROWS = int(math.ceil(1.0 * COUNT / 26))
SCALE = 0.67

cell = min(1.0 * WIDTH / COLS, 1.0 * HEIGHT / ROWS)
cellR = cell * 0.5

# Init SVG
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(WIDTH, HEIGHT), profile='full')

# Backer ref
data = svgu.getDataFromSVG(INPUT_FILE)
dwgBacker = dwg.g(id="backer")
for path in data["paths"]:
    dwgBacker.add(dwg.path(d=path, stroke_width=1.5, stroke="#000000", fill="#FFFFFF"))
dwg.defs.add(dwgBacker)

# Draw forests
x = 0
y = 0
for backer in range(COUNT):
    t = "translate(%s, %s) scale(%s)" % (x,y,SCALE)
    dwg.add(dwg.use("#backer", insert=(0,0), transform=t))
    x += cell
    if x >= (cell*COLS):
        x = 0
        y += cell

dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
