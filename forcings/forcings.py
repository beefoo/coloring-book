# -*- coding: utf-8 -*-

# Sources:
# https://data.giss.nasa.gov/modelforce/
# NASA GISS ModelE2: https://data.giss.nasa.gov/modelE/
# Via: https://www.bloomberg.com/graphics/2015-whats-warming-the-world/

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
parser.add_argument('-forcings', dest="FORCINGS_FILE", default="data/forcings.csv", help="Forcings input file")
parser.add_argument('-observed', dest="OBSERVED_FILE", default="data/observed.csv", help="Observed input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/forcings.svg", help="Path pattern to output svg file")

args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
MARGIN = 50

START_YEAR = 1880
END_YEAR = 2005
BASELINE_YEAR_START = 1880
BASELINE_YEAR_END = 1910
RANGE = (-1, 2)
AXES_W = 70
TICK_LEN = 5
PAD_TOP = 10
FORCING_HEADERS = [
    {"name": "Orbital changes", "label": "Earth's orbital changes"},
    {"name": "Solar", "label": "Solar temperature"},
    {"name": "Volcanic", "label": "Volcanic activity"},
    {"name": "Greenhouse gases", "label": "Greenhouse gases"}
]

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
observed = readCSV(args.OBSERVED_FILE)
forcings = readCSV(args.FORCINGS_FILE)

# convert celsius to fahrenheit
for i, r in enumerate(observed):
    observed[i]["Annual_Mean"] = (9.0/5.0 * r["Annual_Mean"] + 32)

# convert kelvin to fahrenheit
for i, r in enumerate(forcings):
    headers = ["All forcings"] + [h["name"] for h in FORCING_HEADERS]
    for h in headers:
        forcings[i][h] = (9.0/5.0 * r[h]) - 459.67

# get baseline values
def getBaseline(rows, colName, startYear, endYear):
    values = [r[colName] for r in rows if startYear <= r["Year"] <= endYear]
    return mu.mean(values)

fBaseline = getBaseline(forcings, "All forcings", BASELINE_YEAR_START, BASELINE_YEAR_END)
oBaseline = getBaseline(observed, "Annual_Mean", BASELINE_YEAR_START, BASELINE_YEAR_END)

# retrieve data
def getData(rows, colName, startYear, endYear, baseline):
    d = []
    for row in rows:
        if startYear <= row["Year"] <= endYear:
            d.append((row["Year"], row[colName]-baseline))
    return d

rows = []
rows.append({"label": "Observed land and ocean temperature (%s - %s)" % (START_YEAR, END_YEAR), "data": getData(observed, "Annual_Mean", START_YEAR, END_YEAR, oBaseline)})
for header in FORCING_HEADERS:
    rows.append({"label": header["label"], "data": getData(forcings, header["name"], START_YEAR, END_YEAR, fBaseline)})

rowCount = len(rows)
rowHeight = (HEIGHT - MARGIN * (rowCount-1)) / rowCount - 1.0 * PAD_TOP / rowCount

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgLabels = dwg.add(dwg.g(id="labels"))
dwgData = dwg.add(dwg.g(id="data"))

y0 = PAD + rowHeight + PAD_TOP
for ri, r in enumerate(rows):
    y1 = y0 - rowHeight
    yc = y0 - rowHeight / 3.0
    x0 = PAD + AXES_W
    dw = WIDTH - AXES_W
    x1 = x0 + dw

    # draw data
    points = []
    for d in r["data"]:
        xp = mu.norm(d[0], START_YEAR, END_YEAR)
        x = x0 + xp * dw
        yp = mu.norm(d[1], RANGE[0], RANGE[1])
        y = y0 - rowHeight * yp
        points.append((x, y))
    dwgData.add(dwg.polyline(points=points, stroke_width=2, stroke="#000000", fill="none"))

    # draw baseline
    dwgData.add(dwg.line(start=(x0, yc), end=(x1, yc), stroke_width=1, stroke="#000000"))

    # draw axes
    dwgData.add(dwg.line(start=(x0, y0), end=(x0, y1), stroke_width=1, stroke="#000000"))

    # draw axes labels
    r0 = RANGE[0]
    for i in range(RANGE[1]-RANGE[0]+1):
        v = r0 + i
        yp = mu.norm(v, RANGE[0], RANGE[1])
        y = y0 - rowHeight * yp

        # tick
        dwgData.add(dwg.line(start=(x0-TICK_LEN, y), end=(x0, y), stroke_width=1, stroke="#000000"))

        # label
        label = ""
        if v > 0:
            label = "+%s°F" % v
        elif v < 0:
            label = "%s°F" % v

        if len(label) and ri <= 0:
            dwgLabels.add(dwg.text(label, insert=(x0-TICK_LEN*2, y), text_anchor="end", alignment_baseline="middle", font_size=11))
        elif ri <= 0:
            offsetY = 5
            dwgLabels.add(dwg.text("%s-%s" % (BASELINE_YEAR_START, BASELINE_YEAR_END), insert=(x0-TICK_LEN*2, y-offsetY), text_anchor="end", alignment_baseline="middle", font_size=11))
            dwgLabels.add(dwg.text("average", insert=(x0-TICK_LEN*2, y+offsetY), text_anchor="end", alignment_baseline="middle", font_size=11))


    # end line
    p1 = points[-1]
    if p1[1] != yc:
        dwgData.add(dwg.line(start=(x1, yc), end=(x1, p1[1]), stroke_width=1, stroke="#000000", stroke_dasharray="5,2"))

    # draw label
    dwgLabels.add(dwg.text(r["label"], insert=(x0 + 10, y1), text_anchor="start", alignment_baseline="before-edge", font_size=16))
    y0 += MARGIN + rowHeight

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
