# -*- coding: utf-8 -*-

import argparse
import math
from PIL import Image
import svgwrite

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="gridcar/gridcar.%s", help="Input file pattern")
parser.add_argument('-y0', dest="START_YEAR", type=int, default=2001, help="Start year")
parser.add_argument('-y1', dest="END_YEAR", type=int, default=2013, help="End year")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/co2.svg", help="Path to output svg file")

lats = 180
lons = 360
area = lats * lons

args = parser.parse_args()
START_YEAR = args.START_YEAR
END_YEAR = args.END_YEAR
years = END_YEAR - START_YEAR + 1

def mean(data):
    size = len(data)
    if size <= 0:
        return 0
    return sum(data) / size

values = [[] for v in range(area)]
for y in range(years):
    year = START_YEAR + y
    filename = args.INPUT_FILE % year
    yearValues = [float(line.strip())*1000000 for line in open(filename)]
    for i, v in enumerate(yearValues):
        values[i].append(v)
values = [mean(vs) for vs in values]

maxValue = max(values)
print "Max value: %s" % maxValue

im = Image.new("RGB", (lons, lats))
w = lons
h = lats
pixeldata = [(0,0,0) for n in range(len(values))]
for y in range(lats):
    for x in range(lons):
        i = y * w + x
        value = int(values[i] / maxValue * 255)
        if values[i] > 0 and value < 1:
            value = 1
        pixeldata[i] = (value,0,0)
im.putdata(pixeldata)
im.show()
