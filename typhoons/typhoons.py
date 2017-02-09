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

UNITS = [
    {"label": "100", "value": 100},
    {"label": "500", "value": 500},
    {"label": "1,000", "value": 1000}
]
BASE_UNIT = UNITS[0]
MAX_RADIUS = 0.325 * WIDTH
MAX_AREA = math.pi * math.pow(MAX_RADIUS, 2)
ANGLE1 = -10
ANGLE2 = 10
LINE_W = 0.3 * DPI
MIN_R_DIFF = 4

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
data = sorted(data, key=lambda k: -k["Fatalities"])

# Normalize data
maxValue = 1.0 * data[0]["Fatalities"]
height = 0
for i, d in enumerate(data):
    fatalitiesN = d["Fatalities"] / maxValue
    missingN = d["Missing"] / maxValue
    fatalitiesArea = MAX_AREA * fatalitiesN
    missingArea = MAX_AREA * missingN
    fatalitiesR = math.sqrt(fatalitiesArea / math.pi)
    missingR = math.sqrt(missingArea / math.pi)
    if abs(fatalitiesR-missingR) < MIN_R_DIFF:
        if fatalitiesR > missingR:
            fatalitiesR = missingR + MIN_R_DIFF
        else:
            missingR = fatalitiesR + MIN_R_DIFF
    data[i]["fatalitiesR"] = fatalitiesR
    data[i]["missingR"] = missingR
    w = max(fatalitiesR * 2, missingR * 2)
    data[i]["xOffset"] = (WIDTH - w) * 0.5
    height += w

offsetY = 0
MARGIN = 1.0 * (HEIGHT - height) / (len(data)-1)

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgCircles = dwg.add(dwg.g(id="circles"))
dwgLines = dwg.add(dwg.g(id="lines"))
dwgLabels = dwg.add(dwg.g(id="labels"))

x = PAD
y = PAD
data = sorted(data, key=lambda k: k["Year"])
for i, d in enumerate(data):
    maxR = max(d["fatalitiesR"], d["missingR"])
    dx = d["xOffset"]
    dy = offsetY
    center = (x+dx+maxR, y+maxR+dy)
    # draw circles
    fr = d["fatalitiesR"]
    dwgCircles.add(dwg.circle(center=center, r=fr, stroke="#000000", stroke_width=2, fill="none"))
    mr = d["missingR"]
    dwgCircles.add(dwg.circle(center=center, r=mr, stroke="#000000", stroke_width=2, fill="none", stroke_dasharray="5,2"))
    # draw label lines
    dr = maxR - fr
    pf0 = mu.translatePoint(center, math.radians(ANGLE1), fr)
    pm0 = mu.translatePoint(center, math.radians(ANGLE2), mr)
    px = max(pf0[0] + LINE_W, pm0[0] + LINE_W)
    pf1 = (px, pf0[1])
    pm1 = (px, pm0[1])
    dwgLines.add(dwg.line(start=pf0, end=pf1, stroke="#000000", stroke_width=1))
    dwgLines.add(dwg.line(start=pm0, end=pm1, stroke="#000000", stroke_width=1, stroke_dasharray="5,2"))
    # draw labels
    dwgLabels.add(dwg.text("%s dead" % "{:,}".format(d["Fatalities"]), insert=(pf1[0]+2, pf1[1]), text_anchor="start", alignment_baseline="middle", font_size=12))
    dwgLabels.add(dwg.text("%s missing" % "{:,}".format(d["Missing"]), insert=(pm1[0]+2, pm1[1]), text_anchor="start", alignment_baseline="middle", font_size=12))
    # name of typhoon
    dwgLabels.add(dwg.text(d["Name"], insert=(center[0]-maxR-8, center[1]-8), text_anchor="end", alignment_baseline="middle", font_size=12))
    dwgLabels.add(dwg.text(str(d["Year"]), insert=(center[0]-maxR-8, center[1]+8), text_anchor="end", alignment_baseline="middle", font_size=12))
    y += maxR * 2 + MARGIN

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
