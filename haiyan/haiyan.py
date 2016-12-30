# -*- coding: utf-8 -*-

import argparse
import inspect
import math
import os
from PIL import Image
import matplotlib.pyplot as plt
from pprint import pprint
import re
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
parser.add_argument('-imagery', dest="IMAGERY_FILE", default="data/Haiyan_2013-11-07_1430Z_IR-BD_lineless.png", help="Path to input satellite infrared imagery file")
parser.add_argument('-country', dest="COUNTRY_FILE", default="data/map-philippines.svg", help="Path to input svg country file")
parser.add_argument('-pad', dest="PAD", type=int, default=60, help="Padding of output file")
parser.add_argument('-mpa', dest="MIN_POLY_AREA", type=float, default=0.00005, help="Minimum polygon area to match")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/haiyan.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
PAD = args.PAD
MIN_POLY_AREA = args.MIN_POLY_AREA

# Get image data from file
im = Image.open(args.IMAGERY_FILE)
data = list(im.getdata())
(w,h) = im.size
area = w*h

# Create a color matrix normalized between 0.0 and 1.0
colorMatrix = [[0.0]*w for n in range(h)]
for y in range(h):
    for x in range(w):
        colorMatrix[y][x] = 1.0 * data[y*w+x] / 255

def showContours(img, contours):
    # Display the image and plot all contours found
    fig, ax = plt.subplots()
    ax.imshow(img, interpolation='nearest', cmap=plt.cm.gray)
    for n, contour in enumerate(contours):
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
    ax.axis('image')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()

# Retrieve contours
level = 0.45
shapes = measure.find_contours(colorMatrix, level)
print "Found %s shapes using level %s" % (len(shapes), level)
# showContours(colorMatrix, shapes)

# Filter out small shapes
bigShapes = []
for i, shape in enumerate(shapes):
    polyArea = mu.polygonArea(shape)
    p = polyArea / area
    # area is big enough to show
    if p > MIN_POLY_AREA:
        bigShapes.append(shape)
print "Found %s shapes with area > %s" % (len(bigShapes), MIN_POLY_AREA)
# showContours(colorMatrix, bigShapes)

# Init SVG
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(w+PAD*2, h+PAD*2), profile='full')
dwgGroup = dwg.add(dwg.g(id="imagery"))
for i, shape in enumerate(bigShapes):
    points = [(p[1]+PAD,p[0]+PAD) for p in shape]
    # simplify polygon
    target = 0.2 * len(points)
    points = mu.simplify(points, target)
    # smooth polygon
    points = mu.smoothPoints(points, resolution=2, sigma=3)
    # simplify polygon
    points = mu.simplify(points, target)
    # add closure for polygons
    points.append((points[0][0], points[0][1]))
    # add polygon as polyline
    line = dwg.polyline(id="contour"+str(i), points=points, stroke="#000000", stroke_width=1, fill="none")
    dwgGroup.add(line)

# Retrieve country path from svg
country_path_d = None
country_path_w = None
country_path_h = None
with open(args.COUNTRY_FILE, 'rb') as f:
    contents = f.read().replace('\n', '')

    # find the path data
    match = re.search(r'<path id="country_path" d="(.+)"/>', contents)
    if match:
        country_path_d = match.group(1)

    # find the width and height
    match = re.search(r'viewBox="0 0 ([0-9\.]+) ([0-9\.]+)"', contents)
    if match:
        country_path_w = float(match.group(1))
        country_path_h = float(match.group(2))
        print "Country dimensions: %s x %s" % (country_path_w, country_path_h)

if country_path_d is None:
    print "No path found in %s" % args.COUNTRY_FILE
    sys.exit(1)

if country_path_w is None or country_path_h is None:
    print "Could not find width or height in %s" % args.COUNTRY_FILE
    sys.exit(1)

# Add country path to svg
t = "translate(%s,%s) scale(%s)" % (-125.0056, -117.1, 2.9024)
countryGroup = dwg.add(dwg.g(id="country_group", transform=t))
countryGroup.add(dwg.path(id="country", d=country_path_d, stroke="#000000", stroke_width=1.5, fill="none"))

# Save
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
