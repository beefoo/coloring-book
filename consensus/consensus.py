# -*- coding: utf-8 -*-

import argparse
import math
import random
import re
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=int, default=600, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-row', dest="PER_ROW", type=int, default=10, help="Hands per row")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/consensus_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD
PER_ROW = args.PER_ROW

# 97% of publishing climate scientists believe climate change is due to human activity
# source: http://iopscience.iop.org/article/10.1088/1748-9326/11/4/048002
SCIENTIFIC_CONSENSUS = 97

# 48% of U.S. adults believe climate change is due to human activity
# source: http://www.pewinternet.org/2016/10/04/public-views-on-climate-change-and-climate-scientists/
PUBLIC_VIEW = 48

def halton(index, base=3):
    result = 0
    f = 1.0 / base
    i = index
    while i > 0:
      result += f * float(i % base)
      i = math.floor(i / base)
      f = f / float(base)
    return result

def lerp(v1, v2, amount):
    return (v2-v1) * amount + v1

def makeSVG(filename, amount):
    # rows
    total = 100
    scale = 0.8
    rows = int(math.ceil(1.0 * total / PER_ROW))

    # create labels
    yes = ["yes" for l in range(amount)]
    no = ["no" for l in range((total-amount))]
    labels = []
    for row in range(rows):
        for col in range(PER_ROW):
            if not len(no) or len(yes) and row % 2 == 0 and col % 2 == 0 or len(yes) and row % 2 > 0 and col % 2 > 0:
                labels.append(yes.pop())
            else:
                labels.append(no.pop())

    # make equalateral triangle
    cellw = 1.0 * WIDTH / (PER_ROW/2+1)
    cellh = cellw
    halfcell = cellw / 2

    # init svg
    height = rows * cellh
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, height+PAD*2), profile='full')

    # make reference triangle
    dwg.defs.add(dwg.polygon(id="triangle", points=[(0,cellh), (halfcell,0), (cellh,cellh)], fill="none", stroke="#000000", stroke_width=2, stroke_linejoin="round"))
    trianglesGroup = dwg.add(dwg.g(id="triangles"))
    labelsGroup = dwg.add(dwg.g(id="labels"))

    # build
    y = 0
    for row in range(rows):
        x = 0
        direction = 1.0
        if row % 2 > 0:
            direction = -1.0
        for col in range(PER_ROW):
            i = row * PER_ROW + col

            # add triangle
            rotate = 0
            if direction < 0:
                rotate = 180
            t = "translate(%s,%s) scale(%s) rotate(%s %s %s)" % (x+PAD+(1.0-scale)*halfcell, y+PAD+(1.0-scale)*halfcell, scale, rotate, halfcell, halfcell)
            g = dwg.add(dwg.g(id="triangle%s" % i, transform=t))
            g.add(dwg.use("#triangle"))
            trianglesGroup.add(g)

            # add label
            label = labels[i]
            yoffset = direction * 0.15 * cellh
            labelsGroup.add(dwg.text(label, insert=(x+PAD+halfcell, y+PAD+halfcell+yoffset), text_anchor="middle", alignment_baseline="middle", font_size=12))

            # step
            x += halfcell
            direction *= -1
        # y += cellh * (scale+(1.0-scale)*0.5)
        y += cellh * scale

    dwg.save()
    print "Saved svg: %s" % filename


makeSVG(args.OUTPUT_FILE % SCIENTIFIC_CONSENSUS, SCIENTIFIC_CONSENSUS)
makeSVG(args.OUTPUT_FILE % PUBLIC_VIEW, PUBLIC_VIEW)
