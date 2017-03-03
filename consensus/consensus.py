# -*- coding: utf-8 -*-

import argparse
import inspect
import math
import os
import random
import re
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-padx', dest="PADX", type=float, default=0.875, help="Padding of output file")
parser.add_argument('-pady', dest="PADY", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-row', dest="PER_ROW", type=int, default=10, help="Arrow per row")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/consensus_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PADX = args.PADX * DPI
PADY = args.PADY * DPI
WIDTH = args.WIDTH * DPI - PADX * 2
HEIGHT = args.HEIGHT * DPI - PADY * 2
PER_ROW = args.PER_ROW
MARGIN_TOP = 3.25 * DPI

# 97% of publishing climate scientists believe climate change is due to human activity
# source: http://iopscience.iop.org/article/10.1088/1748-9326/11/4/048002
# Cook et al. Consensus on consensus: a synthesis of consensus estimates on human-caused global warming. 2016. Environmental Research Letters, 11.
SCIENTIFIC_CONSENSUS = 97

# 48% of U.S. adults believe climate change is due to human activity
# source: http://www.pewinternet.org/2016/10/04/public-views-on-climate-change-and-climate-scientists/
# Survey conducted May 10-June 6, 2016. The Politics of Climate. Pew Research Center.
PUBLIC_VIEW = 48

def centerOfArrow(arrow):
    xs = [p[0] for p in arrow]
    ys = [p[0] for p in arrow]
    x = (min(xs), max(xs))
    y = (min(ys), max(ys))
    return ((x[1]-x[0])*0.5 + x[0], (y[1]-y[0])*0.5 + y[0])

def normArrow(arrow):
    xs = [p[0] for p in arrow]
    xMin = min(xs)
    xMax = max(xs)
    nArrow = [(mu.norm(p[0], xMin, xMax), p[1]) for p in arrow]
    return nArrow

def makeSVG(filename, amount):
    # rows
    total = 100
    half = total / 2
    rows = int(math.ceil(1.0 * total / PER_ROW))
    yes = amount
    no = total - yes

    # calculate sizes
    cellw = 1.0 * WIDTH / PER_ROW
    cellh = cellw

    # init svg
    width = 1.0 * WIDTH
    height = cellh * rows
    yOffset = PADY
    xOffset = PADX
    if height > HEIGHT:
        scale = HEIGHT / height
        width = width * scale
        cellw = width / PER_ROW
        xOffset = (WIDTH - width) * 0.5 + PADX
    else:
        yOffset = HEIGHT - height + PADY
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PADX*2, HEIGHT+PADY*2), profile='full')
    arrowsGroup = dwg.add(dwg.g(id="arrows"))
    yesGroup = dwg.add(dwg.g(id="yes"))
    noGroup = dwg.add(dwg.g(id="no"))

    # x guides
    xs = [1.0/18, 1.0/9, 2.0/9, 1.0/3, 1.0/2, 5.0/9, 11.0/18, 13.0/18, 5.0/6]
    # y guides
    ys = [1.0/9, 1.0/3, 4.0/9, 5.0/9, 2.0/3, 8.0/9]
    yesArrow = normArrow([
        (0.0, ys[0]), (xs[1], ys[1]), (xs[3], ys[1]),
        (xs[0], ys[-1]), (xs[1], 1.0), (xs[2], 1.0),
        (xs[4], ys[2]), (xs[6], ys[4]), (xs[-1], ys[4]),
        (xs[5], ys[0]), (0.0, ys[0])
    ])
    noArrow = normArrow([
        (xs[5], ys[0]), (xs[-1], ys[4]), (xs[6], ys[4]),
        (xs[4], ys[-1]), (1.0+xs[0], ys[-1]), (1.0+xs[3], ys[1]),
        (1.0+xs[1], ys[1]), (1.0, ys[3]), (xs[7], 0.0),
        (xs[6], 0.0), (xs[5], ys[0])
    ])
    arrowsCombined = [yesArrow, noArrow]
    arrowsLen = len(arrowsCombined)
    yesPoint = centerOfArrow(yesArrow)
    noPoint = centerOfArrow(noArrow)
    radians = mu.radiansBetweenPoints((xs[1]*cellw, 0.0), (xs[5]*cellw, ys[-1]*cellh))
    angle = math.degrees(radians)

    # make reference arrows
    arrowIds = ["yesArrow", "noArrow"]
    for i, arrowId in enumerate(arrowIds):
        arrowGroup = dwg.g(id=arrowId)
        arrow = arrowsCombined[i % arrowsLen]
        points = [(p[0] * cellw, p[1] * cellh) for p in arrow]
        arrowGroup.add(dwg.polygon(points=points, stroke_width=1, stroke="#000000", stroke_linejoin="round", fill="none"))
        dwg.defs.add(arrowGroup)

    # build
    y = yOffset
    for row in range(rows):
        x = xOffset
        for col in range(PER_ROW):
            i = row * PER_ROW + col
            # yes arrow
            if i < yes:
                arrowsGroup.add(dwg.use("#yesArrow", insert=(x, y)))
                p = (yesPoint[0] * cellw + x, yesPoint[1] * cellh + y)
                yesGroup.add(dwg.text("YES", insert=p, text_anchor="middle", alignment_baseline="middle", font_size=9, dominant_baseline="central", transform="rotate(-%s,%s,%s)" % (angle, p[0], p[1])))
            # no arrow
            if i >= (total-no):
                arrowsGroup.add(dwg.use("#noArrow", insert=(x, y)))
                p = (noPoint[0] * cellw + x, noPoint[1] * cellh + y)
                noGroup.add(dwg.text("NO", insert=p, text_anchor="middle", alignment_baseline="middle", font_size=9, dominant_baseline="central", transform="rotate(%s,%s,%s)" % (angle, p[0], p[1])))
            x += cellw
        y += cellh

    dwg.add(dwg.rect(insert=(PADX,PADY), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
    guideY = 2.125 * DPI
    dwg.add(dwg.line(start=(0, guideY), end=(WIDTH+PADX*2, guideY), stroke_width=1, stroke="#000000", fill="none"))

    dwg.save()
    print "Saved svg: %s" % filename

makeSVG(args.OUTPUT_FILE % SCIENTIFIC_CONSENSUS, SCIENTIFIC_CONSENSUS)
makeSVG(args.OUTPUT_FILE % PUBLIC_VIEW, PUBLIC_VIEW)
