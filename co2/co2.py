# -*- coding: utf-8 -*-

import argparse
import inspect
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
parser.add_argument('-in', dest="INPUT_FILE", default="data/global.1751_2013.csv", help="Input file")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width")
parser.add_argument('-height', dest="HEIGHT", type=int, default=1035, help="Height")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding")
parser.add_argument('-years', dest="YEARS", default="1800,1900,2013", help="Years")
parser.add_argument('-rad', dest="RADIUS", type=float, default=5, help="Radius")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/year%s.svg", help="Path pattern to output svg file")

args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
PAD = args.PAD
YEARS = args.YEARS.split(",")
RADIUS = args.RADIUS

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


def makeSVG(filename, value):
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
    dwg.defs.add(dwg.circle(id="circle", center=(0, 0), r=RADIUS, fill="none", stroke="#000000", stroke_width=1))
    for index in range(value):
        hx = mu.halton(index, 3)
        hy = mu.halton(index, 5)
        x = hx * WIDTH + PAD
        y = hy * HEIGHT + PAD
        dwg.add(dwg.use("#circle", insert=(x, y)))
    dwg.save()
    print "Saved svg: %s" % filename

for year in YEARS:
    filename = args.OUTPUT_FILE % year
    makeSVG(filename, data[year])
