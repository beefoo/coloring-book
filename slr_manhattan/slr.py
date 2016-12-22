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
    # out of bounds
    if x < 0 or y < 0 or x >= w or y >= h:
        return False
    land = False
    (r,g,b,a) = data[y*w+x]
    # check alpha
    if a > ALPHA_THRESHOLD:
        (h,s,v) = colorsys.rgb_to_hsv(1.0*r/255, 1.0*g/255, 1.0*b/255)
        # check for non-blue hue
        if h < 0.44 or h > 0.72:
            land = True
    return land

def isEdge(data, x, y, w, h):
    edge = False
    neighbors = [
        # (x-1, y-1),
        (x, y-1),
        # (x+1, y-1),
        (x-1, y),
        (x+1, y),
        # (x-1, y+1),
        (x, y+1),
        # (x+1, y+1)
    ]
    if isLand(data, x, y, w, h):
        matches = 0
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
    edgeData = [(0,0,0) for r in range(w*h)]

    # get shape
    if i <= 0:
        for x in range(w):
            # go from top to bottom
            for y in range(h):
                (r,g,b,a) = data[y*w+x]
                if a > ALPHA_THRESHOLD:
                    shape.append((x,y))
                    edgeData[y*w+x] = (255,0,0)
                    break
            # go from bottom to top
            for y in range(h):
                (r,g,b,a) = data[(h-1-y)*w+x]
                if a > ALPHA_THRESHOLD:
                    shape.append((x,(h-1-y)))
                    edgeData[(h-1-y)*w+x] = (255,0,0)
                    break
        for y in range(h):
            # go from left to right
            for x in range(w):
                (r,g,b,a) = data[y*w+x]
                if a > ALPHA_THRESHOLD:
                    shape.append((x,y))
                    edgeData[y*w+x] = (255,0,0)
                    break
            # go from right to left
            for x in range(w):
                (r,g,b,a) = data[y*w+(w-1-x)]
                if a > ALPHA_THRESHOLD:
                    shape.append(((w-1-x),y))
                    edgeData[y*w+(w-1-x)] = (255,0,0)
                    break
        # remove duplicates
        shape = list(set(shape))
        # simplify shape
        # shape = mu.simplify(shape, 1000)

    # look for white shapes
    edges = [0] * (w*h)
    for y in range(h):
        for x in range(w):
            if isEdge(data, x, y, w, h):
                edges[y*w+x] = 255

    edgeImg = Image.new("RGB", im.size)
    for index,px in enumerate(edgeData):
        if edges[index] > 0:
            edgeData[index] = (255,255,255)
    edgeImg.putdata(edgeData)
    edgeImg.show()

    break
