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
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-row', dest="PER_ROW", type=int, default=10, help="Hands per row")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/consensus_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
PER_ROW = args.PER_ROW
MARGIN_TOP = 3.25 * DPI

# 97% of publishing climate scientists believe climate change is due to human activity
# source: http://iopscience.iop.org/article/10.1088/1748-9326/11/4/048002
SCIENTIFIC_CONSENSUS = 97

# 48% of U.S. adults believe climate change is due to human activity
# source: http://www.pewinternet.org/2016/10/04/public-views-on-climate-change-and-climate-scientists/
PUBLIC_VIEW = 48

def makeSVG(filename, amount):
    # rows
    total = 100
    half = total / 2
    rows = int(math.ceil(1.0 * total / PER_ROW))
    yes = amount
    no = total - yes
    yesLeft = (yes-1) / 2
    yesRight = int(math.ceil((yes-1) * 0.5))
    noLeft = (no-1) / 2
    noRight = int(math.ceil((no-1) * 0.5))
    yesHalf = half
    noHalf = half
    if yes < PER_ROW:
        yesHalf += 5
    if no < PER_ROW:
        noHalf += 5

    # calculate sizes
    cellw = 1.0 * WIDTH / (PER_ROW + (1.0/3))
    cellh = cellw / 1.125

    # init svg
    width = 1.0 * WIDTH
    height = cellh * rows
    yOffset = PAD
    xOffset = PAD
    if height > HEIGHT:
        scale = HEIGHT / height
        width = width * scale
        cellw = width / PER_ROW
        xOffset = (WIDTH - width) * 0.5 + PAD
    else:
        yOffset = min((HEIGHT - height + PAD), MARGIN_TOP)
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
    arrowsGroup = dwg.add(dwg.g(id="arrows"))
    yesGroup = dwg.add(dwg.g(id="yes"))
    noGroup = dwg.add(dwg.g(id="no"))

    # x guides
    xs = [1.0/18, 1.0/9, 2.0/9, 1.0/3, 1.0/2, 5.0/9, 11.0/18, 13.0/18, 5.0/6]
    # y guides
    ys = [1.0/9, 1.0/3, 4.0/9, 5.0/9, 2.0/3, 8.0/9]
    # up and down arrows
    arrowsEven = [
        [
            (0.0, ys[0]), (xs[1], ys[1]), (xs[3], ys[1]),
            (xs[0], ys[-1]), (xs[1], 1.0), (xs[2], 1.0),
            (xs[4], ys[2]), (xs[6], ys[4]), (xs[-1], ys[4]),
            (xs[5], ys[0]), (0.0, ys[0])
        ],[
            (xs[5], ys[0]), (xs[-1], ys[4]), (xs[6], ys[4]),
            (xs[4], ys[-1]), (1.0+xs[0], ys[-1]), (1.0+xs[3], ys[1]),
            (1.0+xs[1], ys[1]), (1.0, ys[3]), (xs[7], 0.0),
            (xs[6], 0.0), (xs[5], ys[0])
        ]
    ]
    arrowsOdd = [
        [(p[0]+0.5, p[1]) for p in arrowsEven[0]],
        [(p[0]-0.5, p[1]) for p in arrowsEven[1]]
    ]
    arrowsCombined = [arrowsEven, arrowsOdd]
    arrowsLen = len(arrowsCombined)
    centerPoints = [
        [(xs[3], ys[3]), (xs[-1], ys[2])],
        [(xs[-1], ys[3]), (xs[3], ys[2])]
    ]
    radians = mu.radiansBetweenPoints((xs[1]*cellw, 0.0), (xs[5]*cellw, ys[-1]*cellh))
    angle = math.degrees(radians)

    # make reference arrows
    arrowIds = ["arrowsEven", "arrowsOdd"]
    for i, arrowId in enumerate(arrowIds):
        arrowGroup = dwg.g(id=arrowId)
        arrows = arrowsCombined[i % arrowsLen]
        for arrow in arrows:
            points = [(p[0] * cellw, p[1] * cellh) for p in arrow]
            arrowGroup.add(dwg.polyline(points=points, stroke_width=1, stroke="#000000", stroke_linejoin="round", fill="none"))
        dwg.defs.add(arrowGroup)

    # build
    y = yOffset
    for row in range(rows):
        x = xOffset
        for col in range(PER_ROW):
            i = row * PER_ROW + col
            # draw arrow
            arrowId = arrowIds[row % 2]
            arrowsGroup.add(dwg.use("#" + arrowId, insert=(x, y)))
            # draw text
            points = [(p[0] * cellw + x, p[1] * cellh + y) for p in centerPoints[row % 2]]
            yesPoint = points[0]
            noPoint = points[1]
            if i >= yesHalf - yesLeft and i <= yesHalf + yesRight:
                yesGroup.add(dwg.text("YES", insert=yesPoint, text_anchor="middle", alignment_baseline="middle", font_size=10, dominant_baseline="central", transform="rotate(-%s,%s,%s)" % (angle, yesPoint[0], yesPoint[1])))
            if i >= noHalf - noLeft and i <= noHalf + noRight:
                noGroup.add(dwg.text("NO", insert=noPoint, text_anchor="middle", alignment_baseline="middle", font_size=10, dominant_baseline="central", transform="rotate(%s,%s,%s)" % (angle, noPoint[0], noPoint[1])))
            x += cellw
        y += cellh

    dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

    dwg.save()
    print "Saved svg: %s" % filename

makeSVG(args.OUTPUT_FILE % SCIENTIFIC_CONSENSUS, SCIENTIFIC_CONSENSUS)
makeSVG(args.OUTPUT_FILE % PUBLIC_VIEW, PUBLIC_VIEW)
