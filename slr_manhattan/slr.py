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
import lib.svgutils as svgu

# input
parser = argparse.ArgumentParser()
# input source: http://choices.climatecentral.org/
parser.add_argument('-input', dest="INPUT_FILE", default="data/slr_%sd.png", help="Path to input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-mpa', dest="MIN_POLY_AREA", type=float, default=0.002, help="Minimum polygon area to match")
parser.add_argument('-image', dest="SHOW_IMAGE", type=bool, default=False, help="Show image")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/manhattan_slr.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
INPUT_FILE = args.INPUT_FILE
OUTPUT_FILE = args.OUTPUT_FILE
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
MIN_POLY_AREA = args.MIN_POLY_AREA
DEGREES = [2, 4]
ALPHA_THRESHOLD = 0.5
SHOW_IMAGE = args.SHOW_IMAGE
MARGIN = 0.25 * DPI
MARGIN_X = -0.175 * DPI
WATER_STEP_X = 0.1 * DPI
WATER_OSCILLATE_X = (0.25*DPI, 0.25*DPI)
WATER_OSCILLATE_Y = (0.05*DPI, 0.2*DPI)
WAVES = 40
WAVE_STEPS_X = 60
WAVE_FREQUENCY = 8.0
LABEL_X = 0.45
LABEL_Y = 0.55

# Init SVG
dwg = svgwrite.Drawing(OUTPUT_FILE, size=(WIDTH + PAD*2, HEIGHT + PAD*2), profile='full')
dwgWater = dwg.add(dwg.g(id="water"))
dwgLand = dwg.add(dwg.g(id="land"))
dwgLabels = dwg.add(dwg.g(id="labels"))

# Draw water
maxWave = max(WATER_OSCILLATE_Y[0], WATER_OSCILLATE_Y[1])
waveHeight = maxWave * 2
waveStepY = 1.0 * HEIGHT / WAVES
yoffset = PAD
xoffset = PAD
if waveHeight > waveStepY:
    diff = waveHeight - waveStepY
    waveStepY = 1.0 * (HEIGHT - diff) / WAVES
    yoffset += diff * 0.5
waveStepY -= (3.0 / WAVES)
waveHStepY = waveStepY * 0.5
waveStepX = 1.0 * WIDTH / (WAVE_STEPS_X-1)
xStart = PAD
xEnd = PAD + WIDTH
waveOffset = 0
for wave in range(WAVES):
    points = []
    x = xoffset
    yh = yoffset + 0.5 * waveStepY
    for xstep in range(WAVE_STEPS_X):
        progress = mu.norm(x+waveOffset, xStart, xEnd)
        amount = mu.lerp(WATER_OSCILLATE_Y[0], WATER_OSCILLATE_Y[1], progress)
        y = yh + mu.oscillate(progress, amount, WAVE_FREQUENCY)
        points.append((x, y))
        # dwgWater.add(dwg.circle(center=(x,y), r=5))
        x += waveStepX
    commands = svgu.pointsToCurve(points)
    dwgWater.add(dwg.path(d=commands, stroke="#000000", stroke_width=1, fill="none"))
    yoffset += waveStepY
    waveOffset += WATER_STEP_X

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

# Contours calculations
count = len(contours)
targetW = 1.0 * (WIDTH - MARGIN_X * (count-1) - MARGIN * 2) / count
targetH = targetW * h / w
scale = 1.0 * targetW / w
offsetY = (HEIGHT - targetH) * 0.5

# Draw contours
xoffset = PAD + MARGIN + 10
yoffset = PAD + offsetY
referenceLines = []
dwgRefrenceGroup = dwgLand.add(dwg.g(id="reference"))
for i, contour in enumerate(contours):
    dwgGroup = dwgLand.add(dwg.g(id=contour["label"]))
    # image as bg
    if SHOW_IMAGE:
        dwgGroup.add(dwg.image(contour["image"], insert=(xoffset, yoffset), size=(targetW, targetH)))
    for j, points in enumerate(contour["shapes"]):
        polyArea = mu.polygonArea(points)
        p = polyArea / area
        # area is big enough to show
        if p > MIN_POLY_AREA:
            points = [(p[1],p[0]) for p in points]
            # simplify polygon
            target = 0.1 * len(points)
            points = mu.simplify(points, target)
            # smooth polygon
            points = mu.smoothPoints(points)
            # simplify polygon
            points = mu.simplify(points, target)
            # add closure for polygons
            points.append((points[0][0], points[0][1]))
            # scale and translate
            points = mu.scalePoints(points, scale)
            points = mu.translatePoints(points, xoffset, yoffset)
            # add polygon
            line = dwg.polygon(id=contour["label"]+str(j), points=points, stroke="#000000", stroke_width=2, fill="#FFFFFF")
            dwgGroup.add(line)
            if i <= 0:
                referenceLines.append(points)
    # add label
    degrees = 0
    if i > 0:
        degrees = DEGREES[i-1]
    labelX = xoffset + targetW * LABEL_X
    labelY = yoffset + targetH * LABEL_Y
    dwgLabels.add(dwg.text("+%s°C" % degrees, insert=(labelX, labelY), text_anchor="middle", font_size=28))
    xoffset += MARGIN_X + targetW

# draw references
xoffset = MARGIN_X + targetW
for d in DEGREES:
    for points in referenceLines:
        # add polygon
        offsetPoints = [(p[0]+xoffset, p[1]) for p in points]
        line = dwg.polygon(id="reference"+str(d), points=offsetPoints, stroke="#000000", stroke_width=1, fill="none", stroke_dasharray="5,2")
        dwgGroup.add(line)
    xoffset += MARGIN_X + targetW

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

# Save
dwg.save()
print "Saved svg: %s" % OUTPUT_FILE
