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
ARCS_W = 0.6

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
    data[i]["value"] = 1.0 * d[dataKey] / maxValue

# Init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgArcs = dwg.add(dwg.g(id="arcs"))

# Init arcs
arcs = 4
arcsI = 1.0 / arcs
stepY = 1.0 * HEIGHT / arcs

rx1 = WIDTH * 0.5
ry1 = stepY
r = min(rx1, ry1)
arcsW = ARCS_W * r
arcW = 1.0 * (arcsW - ARC_MARGIN * (count-1)) / count

# Draw data
for i, d in enumerate(data):
    value = d["value"]
    cx = PAD + WIDTH * 0.5
    cy = stepY + PAD
    for a in range(arcs):
        j = i
        a1 = -90
        a2 = 0
        if a % 2 > 0:
            a1 = 0
            a2 = 90
        # every half turn, arc goes from outer to inner / inner to outer
        if (a/2) % 2 > 0:
            j = count - 1 - i
            a1 = -90
            a2 = -180
            if a % 2 > 0:
                a1 = 180
                a2 = 90
        rx = rx1 - j * (ARC_MARGIN + arcW)
        ry = ry1 - j * (ARC_MARGIN + arcW)
        arcAmount = min(value / arcsI, 1.0)
        if arcAmount > 0:
            ato = mu.lerp(a1, a2, arcAmount)
            commands = svgu.describeArc(cx, cy, rx, ry, a1, ato)
            dwgArcs.add(dwg.path(d=commands, stroke_width=1, stroke="#000000", fill="none"))
        value -= arcsI
        if a % 2 > 0:
            cy += stepY * 2 - arcsW
        if value <=0:
            break

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
