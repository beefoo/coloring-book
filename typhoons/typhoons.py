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
parser.add_argument('-width', dest="WIDTH", type=float, default=11, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=8.5, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/typhoons.svg", help="Path pattern to output svg file")

args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

MAX_RADIUS = 0.25 * HEIGHT
MAX_AREA = math.pi * math.pow(MAX_RADIUS, 2)
LABEL_H_BTM = 0.16 * HEIGHT
LABEL_H_TOP = 0.12 * HEIGHT
MIN_X_MARGIN = 0.45 * DPI
LABEL_H_STEP = 24
MAX_YEAR_STEP = 5
MARGIN_Y = (1.0 * HEIGHT - LABEL_H_BTM - LABEL_H_TOP - MAX_RADIUS * 2) / 3
TIMELINE_Y = PAD + HEIGHT - LABEL_H_BTM - MARGIN_Y
cy = TIMELINE_Y - MARGIN_Y - MAX_RADIUS

if MARGIN_Y <= 0:
    print "Radius is too big!"
    sys.exit(1)

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
labelY0 = PAD + HEIGHT - LABEL_H_BTM
labelY1 = PAD + LABEL_H_TOP

# sort by year
data = sorted(data, key=lambda k: k["Year"])
startYear = data[0]["Year"]
endYear = data[-1]["Year"]
totalYears = endYear - startYear
xStart = PAD + data[0]["radius"]
xEnd = PAD + WIDTH - data[-1]["radius"]
timelineW = xEnd - xStart
yearW = 1.0 * timelineW / totalYears
data = sorted(data, key=lambda k: -k["Year"])

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgLines = dwg.add(dwg.g(id="lines"))
dwgCircles = dwg.add(dwg.g(id="circles"))
dwgLabels = dwg.add(dwg.g(id="labels"))

# Draw timeline
dwgLines.add(dwg.line(start=(xStart, TIMELINE_Y), end=(xEnd, TIMELINE_Y), stroke="#000000", stroke_width=1))

# Draw data
prevLX = MIN_X_MARGIN * -1
labelH = LABEL_H_STEP
for i, d in enumerate(data):
    radius = d["radius"]
    px = mu.norm(d["Year"], startYear, endYear)
    cx = mu.lerp(xStart, xEnd, px)

    # draw circle
    dwgCircles.add(dwg.circle(center=(cx, cy), r=radius, stroke="#000000", stroke_width=2, fill="none"))

    # draw circle on timeline
    dwgCircles.add(dwg.circle(center=(cx, TIMELINE_Y), r=3, fill="#000000"))

    # draw line from circle to timeline
    p1 = (cx, cy+radius)
    p2 = (cx, TIMELINE_Y)
    dwgLines.add(dwg.line(start=p1, end=p2, stroke="#000000", stroke_width=1))

    if i > 0:
        prevYear = data[i-1]["Year"]
        if prevYear - d["Year"] > MAX_YEAR_STEP:
            labelH = LABEL_H_STEP
        else:
            labelH += LABEL_H_STEP

    # draw label line
    lPad = 6
    p3 = (cx, TIMELINE_Y + labelH)
    p4 = (cx + lPad, TIMELINE_Y + labelH)
    dwgLines.add(dwg.polyline([p2, p3, p4], stroke="#000000", stroke_width=1, stroke_dasharray="5,2", fill="none"))

    # draw label
    labelString = d["label"] + " " + str(d["Year"])
    if i >= len(data)-1:
        labelString = d["Type"] + " " + labelString
    lx = p4[0] + lPad
    ly = p4[1]
    dwgLabels.add(dwg.text(labelString, insert=(lx, ly), text_anchor="start", font_size=12, alignment_baseline="middle"));

    # dead or missing
    if i <=0 or i >= len(data)-1:
        ly = labelY1
        labelString = "{:,}".format(d["Combined"])
        dwgLabels.add(dwg.text(labelString, insert=(cx, ly-lPad), text_anchor="start", alignment_baseline="after-edge", font_size=12))
        dwgLabels.add(dwg.text("dead or missing", insert=(cx, ly+lPad), text_anchor="start", alignment_baseline="after-edge", font_size=12))

        # draw label line
        p1 = (cx, ly + lPad * 2)
        p2 = (cx, cy-radius)
        dwgLines.add(dwg.line(start=p1, end=p2, stroke="#000000", stroke_width=1, stroke_dasharray="5,2"))

    prevLX = lx

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
