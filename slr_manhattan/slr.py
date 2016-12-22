# -*- coding: utf-8 -*-

import argparse
import colorsys
import inspect
import os
from PIL import Image
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
# input source: http://choices.climatecentral.org/
parser.add_argument('-input', dest="INPUT_FILE", default="data/slr_%sd.png", help="Path to input file")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/manhattan_slr.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
INPUT_FILE = args.INPUT_FILE
WIDTH = args.WIDTH
PAD = args.PAD
DEGREES = [2, 4]
ALPHA_THRESHOLD = 0.5

def isLand(data, x, y, w, h):
    if x < 0 or y < 0 or x >= w or y >= h:
        return False
    land = False
    (r,g,b,a) = data[y*w+x]
    if a > ALPHA_THRESHOLD:
        (h,s,v) = colorsys.rgb_to_hsv(1.0*r/255, 1.0*g/255, 1.0*b/255)
        if 0.44 > h or h > 0.72:
            land = True
    return land

def isEdge(data, x, y, w, h):
    edge = False
    neighbors = [(x-1, y-1),(x, y-1),(x+1, y-1),(x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)]
    if isLand(data, x, y, w, h):
        for n in neighbors:
            if not isLand(data, n[0], n[1], w, h):
                edge = True
                break
    return edge

shape = []
for i,d in enumerate(DEGREES):
    # get image data
    im = Image.open(INPUT_FILE % d)
    data = list(im.getdata())
    (w,h) = im.size

    # get shape
    if i <= 0:
        for x in range(w):
            # go from top to bottom
            for y in range(h):
                (r,g,b,a) = data[y*w+x]
                if a > ALPHA_THRESHOLD:
                    shape.append((x,y))
                    break
            # go from bottom to top
            for y in range(h):
                (r,g,b,a) = data[(h-1-y)*w+x]
                if a > ALPHA_THRESHOLD:
                    shape.append((x,y))
                    break
        for y in range(h):
            # go from left to right
            for x in range(w):
                (r,g,b,a) = data[y*w+x]
                if a > ALPHA_THRESHOLD:
                    shape.append((x,y))
                    break
            # go from right to left
            for x in range(w):
                (r,g,b,a) = data[y*w+(w-1-x)]
                if a > ALPHA_THRESHOLD:
                    shape.append((x,y))
                    break
        # remove duplicates
        shape = list(set(shape))
        # simplify shape
        shape = simplify(shape, 1000)

    # look for white shapes
    for y in range(h):
        # go from left to right
        for x in range(w):
            if isEdge(data, x, y, w, h):
                edge = True
