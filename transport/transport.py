# -*- coding: utf-8 -*-

# Sources:
# https://docs.google.com/spreadsheets/d/1TAMZLvUrMlxAR4RdDOs928-yoU5RxMrDKIb8tXuOKsc/
# https://www.rita.dot.gov/bts/sites/rita.dot.gov.bts/files/publications/national_transportation_statistics/html/table_04_20.html

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
ARC_MARGIN = 0.05 * DPI
ARC_W = 0.33 * DPI
CENTER_W = 0.1 * WIDTH

def parseNumber(string):
    try:
        num = float(string)
        if "." not in string:
            num = int(string)
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
dataKey = "lc_co2_gpkm"
count = len(data)

# Normalize data
maxValue = max([d[dataKey] for d in data])
for i, d in enumerate(data):
    data[i]["index"] = i
    data[i]["value"] = 1.0 * d[dataKey] / maxValue

def getLineCommands(a, total, target, x, y, td):
    lineAmount = 1.0
    if CENTER_W + total > target:
        lineAmount = 1.0 * (target-total) / CENTER_W
    lineLen = lineAmount * CENTER_W
    direction = -1
    if (a/2) % 2 > 0:
        direction = 1
    lx = x
    ly = y
    lx1 = lx + lineLen * direction
    d = td * ARC_W
    return (["M%s,%s" % (lx, ly), "L%s,%s" % (lx1, ly)],
            ["M%s,%s" % (lx1, ly+d), "L%s,%s" % (lx, ly+d)])

def getConnectors(commands1, commands2):
    # get types
    c1t = (commands1[-1][0], commands1[-2][0])
    c2t = (commands2[0][0], commands2[1][0])
    c3t = (commands2[-1][0], commands2[-2][0])
    c4t = (commands1[0][0], commands1[1][0])
    # get start/end commands
    c1 = commands1[-2]
    c2 = commands2[1]
    c3 = commands2[-2]
    c4 = commands1[1]
    if c2t[1] == "L":
        c2 = commands2[0]
    if c4t[1] == "L":
        c4 = commands1[0]
    # get start/end points
    c1p = tuple([float(p) for p in c1[1:].split(",")[-2:]])
    c2p = tuple([float(p) for p in c2[1:].split(",")[-2:]])
    c3p = tuple([float(p) for p in c3[1:].split(",")[-2:]])
    c4p = tuple([float(p) for p in c4[1:].split(",")[-2:]])
    connector1 = []
    connector2 = []
    if c1t[0] == "L":
        connector1.append(["L%s,%s" % c2p])
    else:
        connector1.append(["M%s,%s" % c1p, "L%s,%s" % c2p])
    if c3t[0] == "L":
        connector2.append(["L%s,%s" % c4p])
    else:
        connector2.append(["M%s,%s" % c3p, "L%s,%s" % c4p])
    return (connector1, connector2)

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgArcs = dwg.add(dwg.g(id="arcs"))

# Calculate arcs
arcs = 4
halfArcs = arcs / 2
arcsI = 1.0 / arcs
arcsW = ARC_W * count + ARC_MARGIN * (count-1)
halfTurnH = 1.0 * ((HEIGHT - ARC_W) + (arcsW - ARC_W) * (halfArcs-1)) / halfArcs
rx1 = (WIDTH - ARC_W*2 - CENTER_W) * 0.5
ry1 = halfTurnH * 0.5

# Calculate longest arc
sortedData = sorted(data, key=lambda k: -k["value"])
j = sortedData[0]["index"]
mrx1 = rx1 - j * (ARC_MARGIN + ARC_W)
mry1 = ry1 - j * (ARC_MARGIN + ARC_W)
j = count - 1 - j
mrx2 = rx1 - j * (ARC_MARGIN + ARC_W)
mry2 = ry1 - j * (ARC_MARGIN + ARC_W)
maxArcLen = CENTER_W * (halfArcs * 1.5) + mu.ellipseCircumference(mrx1, mry1) * 0.5 * (halfArcs/2) + mu.ellipseCircumference(mrx2, mry2) * 0.5 * (halfArcs/2)

# Check for arc validity
if arcsW > rx1:
    print "Arcs too big for page width"
    sys.exit(1)
if arcsW > ry1:
    print "Arcs too big for page height"
    sys.exit(1)

# Init arcs
stepY = halfTurnH - arcsW + ARC_W

# Draw data
for i, d in enumerate(data):
    value = d["value"]
    targetArcLen = value * maxArcLen
    cy = PAD + ry1
    arcCommands = []
    arcCommands2 = [] # runs parallel
    totalArcLen = 0
    for a in range(arcs):
        turnDirection = (a/2) % 2 * -1
        if turnDirection >= 0:
            turnDirection = 1
        cx = PAD + WIDTH * 0.5 + 0.5 * CENTER_W * turnDirection
        j = i
        a1 = -90
        a2 = 0
        if a % 2 > 0:
            a1 = 0
            a2 = 90
        # every half turn, arc goes from outer to inner / inner to outer
        if turnDirection < 0:
            j = count - 1 - i
            a1 = -90
            a2 = -180
            if a % 2 > 0:
                a1 = 180
                a2 = 90
        rx = rx1 - j * (ARC_MARGIN + ARC_W)
        ry = ry1 - j * (ARC_MARGIN + ARC_W)
        # draw first line
        if a <= 0 and CENTER_W > 0:
            cmds = getLineCommands(3, totalArcLen, targetArcLen, cx-CENTER_W, cy-ry, turnDirection)
            arcCommands += cmds[0]
            arcCommands2 = cmds[1] + arcCommands2
            totalArcLen += CENTER_W
            if totalArcLen >= targetArcLen:
                break
        arcLen = mu.ellipseCircumference(rx, ry) * 0.25
        arcAmount = 1.0
        if arcLen + totalArcLen > targetArcLen:
            arcAmount = 1.0 * (targetArcLen-totalArcLen) / arcLen
        if arcAmount > 0:
            ato = mu.lerp(a1, a2, arcAmount)
            commands = svgu.describeArc(cx, cy, rx, ry, a1, ato)
            arcCommands += commands
            d = turnDirection * -1 * ARC_W
            commands = svgu.describeArc(cx, cy, rx+d, ry+d, ato, a1)
            arcCommands2 = commands + arcCommands2
        totalArcLen += arcLen
        if totalArcLen >= targetArcLen:
            break
        if a % 2 > 0:
            # draw line
            if CENTER_W > 0:
                cmds = getLineCommands(a, totalArcLen, targetArcLen, cx, cy + ry, turnDirection * -1)
                arcCommands += cmds[0]
                arcCommands2 = cmds[1] + arcCommands2
                totalArcLen += CENTER_W
                if totalArcLen >= targetArcLen:
                    break
            cy += stepY
    # add connecting commands
    connectors = getConnectors(arcCommands, arcCommands2)
    commands = arcCommands + connectors[0] + arcCommands2 + connectors[1]
    # draw path
    dwgArcs.add(dwg.path(d=commands, stroke_width=1, stroke="#000000", fill="none"))

# dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
