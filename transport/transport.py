# -*- coding: utf-8 -*-

# Sources:
# https://docs.google.com/spreadsheets/d/1TAMZLvUrMlxAR4RdDOs928-yoU5RxMrDKIb8tXuOKsc/
# https://www.rita.dot.gov/bts/sites/rita.dot.gov.bts/files/publications/national_transportation_statistics/html/table_04_20.html

# Icons:
# Freepik: http://www.flaticon.com/packs/vehicles

import argparse
import csv
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
import lib.svgutils as svgu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/emissions_by_mode_of_transport_subset.csv", help="Input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/transport.svg", help="Path pattern to output svg file")

args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
ARC_MARGIN = 0.15 * DPI
ARC_W = 0.25 * DPI
CENTER_W = 0.1 * WIDTH
FOOTPRINT_MARGIN = 0.025 * DPI
ICON_W = 0.625 * DPI

def parseNumber(string):
    try:
        num = float(string)
        return num
    except ValueError:
        return string

def parseNumbers(arr):
    for i, item in enumerate(arr):
        for key in item:
            arr[i][key] = parseNumber(item[key])
    return arr

def readCSV(filename):
    rows = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            lines = [line for line in f if not line.startswith("#")]
            reader = csv.DictReader(lines, skipinitialspace=True)
            rows = list(reader)
            rows = parseNumbers(rows)
    return rows

# Retrieve data
data = readCSV(args.INPUT_FILE)
dataKey = "B2N_lc_co2"
count = len(data)

# Normalize data
maxValue = max([d[dataKey] for d in data])
for i, d in enumerate(data):
    data[i]["index"] = i
    data[i]["value"] = int(d[dataKey])
    data[i]["valueI"] = 1.0 * d[dataKey] / maxValue
    data[i]["svgData"] = svgu.getDataFromSVG("svg/%s" % d["Svg"])

def getArcFootprints(value, cx, cy, rx, ry, a1, a2, w, td):
    footprints = []
    arcLen = mu.ellipseCircumference(rx, ry) * 0.5
    arcAmount = 1.0
    footprintsPerArc = int(1.0 * arcLen / (w+FOOTPRINT_MARGIN))
    arcAmount = min(value, footprintsPerArc)
    footprintAngleStep = 1.0 * w / arcLen
    direction = 1
    if a1 > a2:
        direction = -1
    d = td * -1 * ARC_W
    c = (cx, cy)
    for i in range(arcAmount):
        amount = 1.0 * i / footprintsPerArc
        angle1 = mu.lerp(a1, a2, amount)
        angle2 = mu.lerp(a1, a2, amount+footprintAngleStep)
        d1 = mu.ellipseRadius(rx, ry, angle1)
        d2 = mu.ellipseRadius(rx, ry, angle2)
        p1 = mu.translatePoint(c, math.radians(angle1), d1)
        p2 = mu.translatePoint(c, math.radians(angle1), d1+d)
        p3 = mu.translatePoint(c, math.radians(angle2), d2+d)
        p4 = mu.translatePoint(c, math.radians(angle2), d2)
        footprints.append([p1, p2, p3, p4, p1])
    return footprints

def getLineFootprints(a, value, x, y, w, td):
    footprints = []
    amount = int(round(1.0 * CENTER_W / (w + FOOTPRINT_MARGIN)))
    lineAmount = min(amount, value)
    m = 1.0 * (CENTER_W - amount * w) / amount
    direction = -1
    if a % 2 > 0:
        direction = 1
    d = td * ARC_W
    lx = x
    ly = y
    for i in range(lineAmount):
        footprints.append([(lx, ly), (lx, ly+d), (lx+w*direction, ly+d), (lx+w*direction, ly), (lx, ly)])
        lx += direction * (w + m)
    return footprints

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgFootprints = dwg.add(dwg.g(id="footprints"))
dwgIcons = dwg.add(dwg.g(id="icons"))
dwgLabels = dwg.add(dwg.g(id="labels"))

# Calculate arcs
arcs = 2
halfArcs = arcs / 2
arcsI = 1.0 / arcs
arcsW = ARC_W * count + ARC_MARGIN * (count-1)
halfTurnH = 1.0 * ((HEIGHT - ARC_W) + (arcsW - ARC_W) * (arcs-1)) / arcs
rx1 = (WIDTH - ARC_W*2 - CENTER_W) * 0.5
ry1 = halfTurnH * 0.5

# Calculate longest arc
sortedData = sorted(data, key=lambda k: -k["valueI"])
maxTransport = sortedData[0]
j = maxTransport["index"]
mrx1 = rx1 - j * (ARC_MARGIN + ARC_W)
mry1 = ry1 - j * (ARC_MARGIN + ARC_W)
j = count - 1 - j
mrx2 = rx1 - j * (ARC_MARGIN + ARC_W)
mry2 = ry1 - j * (ARC_MARGIN + ARC_W)
maxArcLen = CENTER_W * (arcs + 1) + mu.ellipseCircumference(mrx1, mry1) * 0.5 * halfArcs + mu.ellipseCircumference(mrx2, mry2) * 0.5 * halfArcs
stepY = halfTurnH - arcsW + ARC_W
footprintW = 1.0 * (maxArcLen - FOOTPRINT_MARGIN * (maxTransport["value"]-1)) / maxTransport["value"] * 0.975

# Check for arc validity
if footprintW <= 0:
    print "Footprint margin to big"
    sys.exit(1)
if arcsW > rx1:
    print "Arcs too big for page width"
    sys.exit(1)
if arcsW > ry1:
    print "Arcs too big for page height"
    sys.exit(1)

# Draw data
for i, d in enumerate(data):

    # add icons
    svgd = d["svgData"]
    w = svgd["width"]
    h = svgd["height"]
    scale = 1.0 * ICON_W / w
    th = h * scale
    ty = PAD + i * (ARC_W + ARC_MARGIN) - (th - ARC_W) * 0.5
    tx = PAD + WIDTH * 0.5 - 0.5 * CENTER_W - ICON_W - 10
    t = "translate(%s, %s) scale(%s)" % (tx, ty, scale)
    g = dwgIcons.add(dwg.g(id="icon%s" % i, transform=t))
    strokeW = 1.0 / scale
    for path in svgd["paths"]:
        g.add(dwg.path(d=path, fill="#000000"))

    # add label
    ty = PAD + i * (ARC_W + ARC_MARGIN)
    dwgLabels.add(dwg.text(d["Label"], insert=(tx - 10, ty), text_anchor="end", alignment_baseline="before-edge", font_size=14))

    value = d["value"]
    cy = PAD + ry1
    footprints = []
    for a in range(arcs):
        turnDirection = a % 2 * -1
        if turnDirection >= 0:
            turnDirection = 1
        cx = PAD + WIDTH * 0.5 + 0.5 * CENTER_W * turnDirection
        j = i
        a1 = -90
        a2 = 90

        # every half turn, arc goes from outer to inner / inner to outer
        if turnDirection < 0:
            j = count - 1 - i
            a1 = -90
            a2 = -270
        rx = rx1 - j * (ARC_MARGIN + ARC_W)
        ry = ry1 - j * (ARC_MARGIN + ARC_W)

        # draw first line
        if a <= 0 and CENTER_W > 0:
            fs = getLineFootprints(1, value, cx-CENTER_W, cy-ry, footprintW, turnDirection)
            footprints += fs
            value -= len(fs)
            if value < 0:
                break

        # draw arc
        fs = getArcFootprints(value, cx, cy, rx, ry, a1, a2, footprintW, turnDirection)
        footprints += fs
        value -= len(fs)
        if value < 0:
            break

        # draw line
        if CENTER_W > 0:
            fs = getLineFootprints(a, value, cx, cy + ry, footprintW, turnDirection * -1)
            footprints += fs
            value -= len(fs)
            if value < 0:
                break

        cy += stepY

    print len(footprints)
    # draw path
    for footprint in footprints:
        dwgFootprints.add(dwg.polygon(points=footprint, stroke_width=1, stroke="#000000", fill="none"))

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
