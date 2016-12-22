# -*- coding: utf-8 -*-

import argparse
import colorsys
import inspect
import matplotlib.pyplot as plt
import os
from PIL import Image
from skimage import measure
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

def inBounds(x, y, w, h):
    return x >= 0 and y >= 0 and x < w and y < h

def isLand(data, x, y, w, h):
    if not inBounds(x, y, w, h):
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

def isShape(data, x, y, w, h):
    (r,g,b,a) = data[y*w+x]
    # check alpha
    if a > 0:
        return True
    return False

def isWater(data, x, y, w, h):
    # out of bounds
    if not inBounds(x, y, w, h):
        return False
    (r,g,b,a) = data[y*w+x]
    return a > ALPHA_THRESHOLD and not isLand(data, x, y, w, h)

def showContours(img, contours):
    # Display the image and plot all contours found
    fig, ax = plt.subplots()
    ax.imshow(img, interpolation='nearest', cmap=plt.cm.gray)
    for n, contour in enumerate(contours):
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
        break
    ax.axis('image')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()

# retrieve contours
contours = []
for i,d in enumerate(DEGREES):
    # get image data
    im = Image.open(INPUT_FILE % d)
    data = list(im.getdata())
    (w,h) = im.size

    # get shape
    if i <= 0:
        shape = [[0.0]*w for n in range(h)]
        for y in range(h):
            for x in range(w):
                if isShape(data, x, y, w, h):
                    shape[y][x] = 1.0
        shapeContours = measure.find_contours(shape, 0.2)
        contours.append({
            "label": "0d",
            "contours": shapeContours
        })
        # showContours(shape, shapeContours)

    # get land
    land = [[0.0]*w for n in range(h)]
    for y in range(h):
        for x in range(w):
            if isLand(data, x, y, w, h):
                land[y][x] = 1.0

    landContours = measure.find_contours(land, 0.2)
    # showContours(land, landContours)
    contours.append({
        "label": "%sd" % d,
        "contours": landContours
    })

# Draw contours
