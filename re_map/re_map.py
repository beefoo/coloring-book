# -*- coding: utf-8 -*-

# Solar source
# NREL - Solar Summaries: Spreadsheet of annual 10-Kilometer solar data (DNI, LATTILT and GHI) data by state and zip code
# http://www.nrel.gov/gis/data_solar.html

# Wind source
# NREL - United States Wind Power Class - no exclusions - 50m
# http://www.nrel.gov/gis/data_wind.html
# http://www.nrel.gov/gis/wind_detail.html

import argparse
import csv
import inspect
import json
import math
import os
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.geoutils as gu
import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-geo', dest="GEO_FILE", default="data/us_lng_lats.csv", help="Lat/lng input file")
parser.add_argument('-width', dest="WIDTH", type=float, default=11, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=8.5, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/re_map_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

# config
CONFIG = {
    "solar": {
        "file": "data/lat_lng_ghi.csv",
        "pattern": "star"
    },
    "wind": {
        "file": "data/lat_lng_wind.csv",
        "pattern": "wave"
    }
}
LABELS = {
    "solar": [
        {"display": "1", "value": 3.5, "description": "", "color": "#000000"},
        {"display": "2", "value": 4, "description": "", "color": "#333333"},
        {"display": "3", "value": 4.5, "description": "", "color": "#666666"},
        {"display": "4", "value": 5, "description": "", "color": "#999999"},
        {"display": "5", "value": 5.5, "description": "", "color": "#CCCCCC"},
        {"display": "6", "value": 6, "description": "", "color": "#FFFFFF"}
    ],
    "wind": [
        {"display": "1", "value": 1, "description": "", "color": "#FFFFFF"},
        {"display": "2", "value": 2, "description": "", "color": "#CCCCCC"},
        {"display": "3", "value": 3, "description": "", "color": "#999999"},
        {"display": "4", "value": 4, "description": "", "color": "#666666"},
        {"display": "5", "value": 5, "description": "", "color": "#333333"},
        {"display": "6", "value": 6, "description": "", "color": "#000000"}
    ]
}

def getLabel(labels, value):
    label = labels[-1]
    for l in labels:
        if value <= l["value"]:
            label = l
            break
    return label.copy()

def nearestNeighborsValue(point, matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    (i, j) = point
    neighbors = [(i-1, j-1), (i, j-1), (i+1, j-1),
                 (i-1, j  ),           (i+1, j  ),
                 (i-1, j+1), (i, j+1), (i+1, j+1)]
    values = []
    for n in neighbors:
        (x, y) = n
        if y < rows and x < cols and y >= 0 and x >= 0 and matrix[y][x] >= 0:
            values.append(matrix[y][x])
    return mu.mean(values)


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

# retrieve geo coordinates
cc = readCSV(args.GEO_FILE)
validCoordinates = [(c["lng"], c["lat"]) for c in cc]

def makeMap(name, coordinates):
    global CONFIG
    global LABELS

    filename = CONFIG[name]["file"]
    pattern = CONFIG[name]["pattern"]
    labels = LABELS[name]
    data = readCSV(filename)

    # Init svg
    outfilename = args.OUTPUT_FILE % name
    dwg = svgwrite.Drawing(outfilename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
    dwgCells = dwg.add(dwg.g(id="cells"))
    dwgLabels = dwg.add(dwg.g(id="labels"))

    # get bounds, ratio
    bounds = gu.getBounds(coordinates)
    (rw, rh) = gu.getRatio(coordinates)

    # make calculations
    width = 1.0 * WIDTH
    height = width * rh / rw
    lngDiff = abs(bounds[2]-bounds[0])
    latDiff = abs(bounds[3]-bounds[1])
    cellW = width / (lngDiff+1)
    cellH = height / (latDiff+1)
    rows = int(width / cellW)
    cols = int(height / cellH)
    halfW = cellW * 0.5
    halfH = cellH * 0.5
    offsetX = PAD
    offsetY = PAD + HEIGHT - height

    # make a value matrix
    valueMatrix = [[-1 for i in xrange(cols)] for j in xrange(rows)]
    for d in data:
        x = int(d["lng"] - bounds[0])
        y = int(d["lat"] - bounds[1])
        if y < rows and x < cols and y >= 0 and x >= 0:
            valueMatrix[y][x] = d["value"]

    # go through each coordinate
    lnglats = []
    for c in coordinates:
        (lng, lat) = c
        dp = next((d for d in data if d["lng"]==lng and d["lat"]==lat), None)
        (x, y) = gu.coordinateToPixel((lng+0.5, lat+0.5), width-cellW, height-cellH, bounds)
        x += offsetX
        y += offsetY

        # data point not found; guess
        if dp is None:
            nx = int(lng - bounds[0])
            ny = int(lat - bounds[1])
            nnValue = nearestNeighborsValue((nx, ny), valueMatrix)
            label = getLabel(labels, nnValue)
            # label["color"] = "red"

        # data point found
        else:
            label = getLabel(labels, dp["value"])

        color = label["color"]
        points = [(x,y-halfW), (x+halfW,y), (x,y+halfW), (x-halfW,y), (x,y-halfW)]
        dwgCells.add(dwg.polygon(id="l%s_%s" % c, points=points, fill=color, stroke="#000000", stroke_width=1))
        lnglats.append("%s,%s" % c)

    dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
    dwg.save()
    print "Saved svg: %s" % outfilename
    return lnglats

lnglats1 = makeMap("solar", validCoordinates)
lnglats2 = makeMap("wind", validCoordinates)

# lnglats = [l.split(",") for l in list(set(lnglats1 + lnglats2))]
# lnglats = sorted(lnglats, key=lambda lnglat: lnglat[1])
# lnglats = sorted(lnglats, key=lambda lnglat: lnglat[0])
# with open("data/us_lng_lats.csv", 'wb') as f:
#     w = csv.writer(f, delimiter=',')
#     w.writerow(['lng', 'lat'])
#     for lnglat in lnglats:
#         w.writerow(lnglat)
