# -*- coding: utf-8 -*-

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

# input
parser = argparse.ArgumentParser()
# Source: http://cdiac.ornl.gov/trends/emis/tre_glob_2013.html
# Unit: One million metric tons of carbon
parser.add_argument('-in', dest="INPUT_FILE", default="data/typhoons.csv", help="Input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/typhoons.svg", help="Path pattern to output svg file")

args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

MAX_RADIUS = 0.275 * WIDTH
MAX_AREA = math.pi * math.pow(MAX_RADIUS, 2)
LABEL_MARGIN = 0.333 * DPI
LABEL_MARGIN_RIGHT = 0.25 * DPI
MIN_Y_MARGIN = 0.45 * DPI
cx = PAD + WIDTH * 0.533

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
    with open(filename, 'rb') as f:
        lines = [line for line in f if not line.startswith("#")]
        reader = csv.DictReader(lines, skipinitialspace=True)
        rows = list(reader)
        rows = parseNumbers(rows)
    return rows

data = readCSV(args.INPUT_FILE)
data = sorted(data, key=lambda k: -k["Combined"])

# Normalize data
maxValue = 1.0 * data[0]["Combined"]
for i, d in enumerate(data):
    percent = d["Combined"] / maxValue
    area = MAX_AREA * percent
    radius = math.sqrt(area / math.pi)
    data[i]["radius"] = radius
    add = ""
    if len(d["PhilName"]):
        add = " ("+d["PhilName"]+")"
    # data[i]["label"] = d["Type"] + " " + d["Name"] + add
    data[i]["label"] = d["Name"] + add

# labels should be right aligned to largest circle
labelX0 = cx - data[0]["radius"] - LABEL_MARGIN
labelX1 = cx + data[0]["radius"] + LABEL_MARGIN_RIGHT

# sort by year
data = sorted(data, key=lambda k: k["Year"])
startYear = data[0]["Year"]
endYear = data[-1]["Year"]
totalYears = endYear - startYear
yStart = PAD + data[0]["radius"]
yEnd = PAD + HEIGHT - data[-1]["radius"]
timelineH = yEnd - yStart
yearH = 1.0 * timelineH / totalYears

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgLines = dwg.add(dwg.g(id="lines"))
dwgCircles = dwg.add(dwg.g(id="circles"))
dwgLabels = dwg.add(dwg.g(id="labels"))

# Draw timeline
dwgLines.add(dwg.line(start=(cx, yStart), end=(cx, yEnd), stroke="#000000", stroke_width=1))

# Draw data
prevLY = MIN_Y_MARGIN * -1
for i, d in enumerate(data):
    radius = d["radius"]
    py = mu.norm(d["Year"], startYear, endYear)
    cy = mu.lerp(yStart, yEnd, py)
    center = (cx, cy)
    # draw circle
    dwgCircles.add(dwg.circle(center=center, r=3, fill="#000000"))
    dwgCircles.add(dwg.circle(center=center, r=radius, stroke="#000000", stroke_width=2, fill="none"))

    # name of typhoon
    lx = labelX0
    ly = cy
    if ly < prevLY + MIN_Y_MARGIN:
        ly = prevLY + MIN_Y_MARGIN
    lPad = 6
    labelString = d["label"]
    if i <= 0:
        labelString = d["Type"] + " " + labelString
    dwgLabels.add(dwg.text(labelString, insert=(lx, ly-lPad), text_anchor="end", alignment_baseline="middle", font_size=12))
    dwgLabels.add(dwg.text(str(d["Year"]), insert=(lx, ly+lPad), text_anchor="end", alignment_baseline="middle", font_size=12))

    # draw label line
    p1 = (lx + lPad, ly)
    p2 = (cx, cy)
    dwgLines.add(dwg.line(start=p1, end=p2, stroke="#000000", stroke_width=1, stroke_dasharray="5,2"))

    # dead or missing
    if i <=0 or i >= len(data)-1:
        lx = labelX1
        labelString = "{:,}".format(d["Combined"])
        dwgLabels.add(dwg.text(labelString, insert=(lx, cy-lPad), text_anchor="start", alignment_baseline="middle", font_size=12))
        dwgLabels.add(dwg.text("dead or missing", insert=(lx, cy+lPad), text_anchor="start", alignment_baseline="middle", font_size=12))

        # draw label line
        p1 = (lx - lPad, cy)
        p2 = (cx + radius, cy)
        dwgLines.add(dwg.line(start=p1, end=p2, stroke="#000000", stroke_width=1, stroke_dasharray="5,2"))

    prevLY = ly

def getGuideRadius(amt):
    p = 1.0 * amt / maxValue
    area = MAX_AREA * p
    return math.sqrt(area / math.pi)

# make a circle for scale
gx = 0.2 * WIDTH + PAD
gy = 0.25 * HEIGHT + PAD
# dwgGuide = dwg.add(dwg.g(id="guide"))
# dwgGuide.add(dwg.circle(center=(gx, gy), r=getGuideRadius(100), stroke="#000000", stroke_width=2, fill="none"))
# dwgGuide.add(dwg.circle(center=(gx, gy), r=getGuideRadius(500), stroke="#000000", stroke_width=2, fill="none"))
# dwgGuide.add(dwg.circle(center=(gx, gy), r=getGuideRadius(1000), stroke="#000000", stroke_width=2, fill="none"))
# dwgGuide.add(dwg.circle(center=(gx, gy), r=getGuideRadius(2500), stroke="#000000", stroke_width=2, fill="none"))
# dwgGuide.add(dwg.circle(center=(gx, gy), r=getGuideRadius(5000), stroke="#000000", stroke_width=2, fill="none"))

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
