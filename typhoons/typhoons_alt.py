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

LABELS = [
    {"display": "1", "value": 500, "description": "Under 500", "color": "yellow"},
    {"display": "2", "value": 1000, "description": "500 to 1,000", "color": "orange"},
    {"display": "3", "value": 2500, "description": "1,000 to 2,500", "color": "red"},
    {"display": "4", "value": 5000, "description": "2,500 to 5,000", "color": "magenta"},
    {"display": "5", "value": 10000, "description": "Over 5,000", "color": "violet"}
]
START_YEAR = 1950
END_YEAR = 2016
MIN_YEAR_MARGIN = 0.05 * DPI

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

def getLabel(value, labels):
    label = labels[-1]
    for l in labels:
        if value <= l["value"]:
            label = l
            break
    return label.copy()

data = readCSV(args.INPUT_FILE)
data = sorted(data, key=lambda k: k["Year"])

# Normalize data
minYear = data[0]["Year"]
maxYear = data[-1]["Year"]
minDecade = minYear / 10
maxDecade = maxYear / 10
decades = maxDecade - minDecade + 1
for i, d in enumerate(data):
    data[i]["label"] = getLabel(d["Combined"], LABELS)
    data[i]["decade"] = d["Year"] / 10 - minDecade
    data[i]["index"] = i
    data[i]["center"] = (0,0)

# calculations
decadeHeight = 1.0 * HEIGHT / decades
yearWidth = 1.0 * WIDTH / 10
yearDiameter = WIDTH * 0.1
yearRadius = yearDiameter * 0.5

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgTimeline = dwg.add(dwg.g(id="timeline"))
dwgCircles = dwg.add(dwg.g(id="circles"))
dwgLabels = dwg.add(dwg.g(id="labels"))
dwgNames = dwg.add(dwg.g(id="names"))

# Init label groups
dwgLabelGroups = {}
for l in LABELS:
    dwgLabelGroups[l["display"]] = dwgLabels.add(dwg.g(id="labels%s" % l["display"]))

# Draw timeline
timelineW = WIDTH - yearDiameter
timelineX = PAD + yearRadius
maxX = timelineX + timelineW
for d in range(decades):
    timelineY = PAD + d * decadeHeight + decadeHeight - yearRadius
    start = (timelineX, timelineY)
    end = (maxX, timelineY)
    if d >= decades-1:
        xi = END_YEAR % 10
        end = (PAD + yearWidth * xi + yearWidth * 0.5, timelineY)
        dwgTimeline.add(dwg.line(start=start, end=end, stroke="#000000", stroke_width=2))
    else:
        dwgTimeline.add(dwg.line(start=start, end=end, stroke="#000000", stroke_width=2))

# Determine positions
for d in range(decades):
    years = [h for h in data if h["decade"]==d]
    prevYears = []
    y = PAD + d * decadeHeight + decadeHeight - yearRadius
    for year in years:
        i = year["Year"] % 10
        x = PAD + yearWidth * i + yearWidth * 0.5
        if len(prevYears):
            prev = prevYears[-1]
            prevXMin = prev[0] + yearDiameter + MIN_YEAR_MARGIN
            if x < prevXMin:
                x = prevXMin
        data[year["index"]]["center"] = (x, y)
        prevYears.append((x, y))
    # reverse list
    prevYears = list(reversed(prevYears))
    years = list(reversed(years))
    for i, p in enumerate(prevYears):
        year = years[i]
        if p[0] > maxX:
            center = (maxX, y)
            prevYears[i] = center
            data[year["index"]]["center"] = center
        if i > 0:
            prev = prevYears[i-1]
            prevXMax = prev[0] - yearDiameter - MIN_YEAR_MARGIN
            if p[0] > prevXMax:
                center = (prevXMax, p[1])
                prevYears[i] = center
                data[year["index"]]["center"] = center

# Draw data
for d in data:
    # draw circle
    dwgCircles.add(dwg.circle(center=d["center"], r=yearRadius, stroke="#000000", stroke_width=2, fill="#FFFFFF"))

    # draw label
    label = d["label"]
    dwgLabelGroups[label["display"]].add(dwg.text(label["display"], insert=d["center"], text_anchor="middle", alignment_baseline="middle", font_size=14))

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
