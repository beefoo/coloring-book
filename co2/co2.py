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

import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
# Source: http://cdiac.ornl.gov/trends/emis/tre_glob_2013.html
# Unit: One million metric tons of carbon
parser.add_argument('-in', dest="INPUT_FILE", default="data/global.1751_2013.csv", help="Input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-years', dest="YEARS", default="1800,1900,2013", help="Years")
parser.add_argument('-rad', dest="RADIUS", type=float, default=5, help="Radius")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/year%s.svg", help="Path pattern to output svg file")

args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
YEARS = args.YEARS.split(",")
RADIUS = args.RADIUS
LABEL_H = 50

# Retrieve data
data = {}
with open(args.INPUT_FILE) as f:
    lines = f.readlines()
    # skip header and notes
    lines.pop(0)
    lines.pop(0)
    for line in lines:
        cols = line.split(",")
        data[cols[0]] = int(cols[1])

def makeSVG(filename, value, label):
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
    dwg.defs.add(dwg.circle(id="circle", center=(0, 0), r=RADIUS, fill="#FFFFFF", stroke="#000000", stroke_width=1))
    dwgCircles = dwg.add(dwg.g(id="circles"))
    cx = WIDTH * 0.5 + PAD
    cy = (HEIGHT - LABEL_H) * 0.5 + PAD + LABEL_H
    maxR = WIDTH * 0.5 - RADIUS*2
    # draw label
    dwg.add(dwg.text(label, insert=(cx, PAD+LABEL_H*0.5), text_anchor="middle", alignment_baseline="before-edge", font_size=28))
    dwg.add(dwg.circle(center=(cx, cy), r=(WIDTH * 0.5), fill="none", stroke="#000000", stroke_width=2))
    # draw circles
    for index in range(value):
        ha = mu.halton(index, 3)
        hr = mu.halton(index, 5)
        angle = ha * 360
        distance = hr * maxR
        p = mu.translatePoint((cx, cy), math.radians(angle), distance)
        dwgCircles.add(dwg.use("#circle", insert=p))
    dwg.save()
    print "Saved svg: %s" % filename

for year in YEARS:
    filename = args.OUTPUT_FILE % year
    makeSVG(filename, data[year], "%s carbon emissions from fossil fuels" % year)
