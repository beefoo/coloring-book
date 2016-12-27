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
parser.add_argument('-mpa', dest="MIN_POLY_AREA", type=float, default=0.002, help="Minimum polygon area to match")
parser.add_argument('-image', dest="SHOW_IMAGE", type=bool, default=False, help="Show image")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/manhattan_slr.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
INPUT_FILE = args.INPUT_FILE
OUTPUT_FILE = args.OUTPUT_FILE
WIDTH = args.WIDTH
PAD = args.PAD
MIN_POLY_AREA = args.MIN_POLY_AREA
DEGREES = [2, 4]
ALPHA_THRESHOLD = 0.5
SHOW_IMAGE = args.SHOW_IMAGE

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

def isShape(data, x, y, w, h):
    (r,g,b,a) = data[y*w+x]
    # check alpha
    if a > 0:
        return True
    return False

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

contours = []

# get overall shape
referenceFile = INPUT_FILE % DEGREES[0]
im = Image.open(referenceFile)
data = list(im.getdata())
(w,h) = im.size
area = w*h
shape = [[0.0]*w for n in range(h)]
for y in range(h):
    for x in range(w):
        if isShape(data, x, y, w, h):
            shape[y][x] = 1.0
shapeContours = measure.find_contours(shape, 0.2)
contours.append({
    "label": "land_0d",
    "image": referenceFile.split("/")[1],
    "shapes": shapeContours
})
# showContours(shape, shapeContours)

for i,d in enumerate(DEGREES):
    # get image data
    filename = INPUT_FILE % d
    im = Image.open(filename)
    data = list(im.getdata())

    # get land
    land = [[0.0]*w for n in range(h)]
    for y in range(h):
        for x in range(w):
            if isLand(data, x, y, w, h):
                land[y][x] = 1.0

    landContours = measure.find_contours(land, 0.2)
    # showContours(land, landContours)
    contours.append({
        "label": "land_%sd" % d,
        "image": filename.split("/")[1],
        "shapes": landContours
    })

# Init SVG
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(w*len(contours), h), profile='full')

# Draw contours
xoffset = 0
for contour in contours:
    dwgGroup = dwg.add(dwg.g(id=contour["label"]))
    # image as bg
    if SHOW_IMAGE:
        dwgGroup.add(dwg.image(contour["image"], insert=(xoffset, 0), size=(w, h)))
    for i, points in enumerate(contour["shapes"]):
        polyArea = mu.polygonArea(points)
        p = polyArea / area
        # area is big enough to show
        if p > MIN_POLY_AREA:
            points = [(p[1]+xoffset,p[0]) for p in points]
            # simplify polygon
            target = 0.1 * len(points)
            points = mu.simplify(points, target)
            # smooth polygon
            points = mu.smoothPoints(points)
            # simplify polygon
            points = mu.simplify(points, target)
            # add closure for polygons
            points.append((points[0][0], points[0][1]))
            # add polygon as polyline
            line = dwg.polyline(id=contour["label"]+str(i), points=points, stroke="#000000", stroke_width=2, fill="none")
            dwgGroup.add(line)
    xoffset += w
# Save
dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
