# -*- coding: utf-8 -*-

import argparse
import calendar
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
# input source: https://www.ncdc.noaa.gov/monitoring-references/faq/anomalies.php
parser.add_argument('-input', dest="INPUT_FILE", default="data/188001-201612_land_ocean.csv", help="Path to input file")
parser.add_argument('-ys', dest="YEAR_START", type=int, default=1986, help="Year start on viz")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=1200, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=60, help="Padding of output file")
parser.add_argument('-rank', dest="MAX_RANK", type=int, default=9, help="Maximum rank to display")
parser.add_argument('-wavex', dest="WAVELENGTH_X", type=float, default=30.0, help="Wavelength to oscillate x")
parser.add_argument('-wavey', dest="WAVELENGTH_Y", type=float, default=15.0, help="Wavelength to oscillate y")
parser.add_argument('-freqx', dest="FREQUENCY_X", type=float, default=4.0, help="Frequency to oscillate x")
parser.add_argument('-freqy', dest="FREQUENCY_Y", type=float, default=2.0, help="Frequency to oscillate y")
parser.add_argument('-edge', dest="EDGE", type=float, default=15.0, help="Jagged edge height")
parser.add_argument('-ylabel', dest="YLABEL_WIDTH", type=float, default=100.0, help="Y-label width")
parser.add_argument('-xlabel', dest="XLABEL_HEIGHT", type=float, default=50.0, help="X-label height")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/188001-201612_land_ocean.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
YEAR_START = args.YEAR_START
PAD = args.PAD
MAX_RANK = args.MAX_RANK
WAVELENGTH_X = args.WAVELENGTH_X
WAVELENGTH_Y = args.WAVELENGTH_Y
FREQUENCY_X = args.FREQUENCY_X
FREQUENCY_Y = args.FREQUENCY_Y
EDGE = args.EDGE
YLABEL_WIDTH = args.YLABEL_WIDTH
XLABEL_HEIGHT = args.XLABEL_HEIGHT

values = []
months = [[] for m in range(12)]

# read csv
with open(args.INPUT_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    for skip in range(4):
        next(r, None)
    # for each row
    for _year,_value in r:
        value = {
            "index": len(values),
            "key": _year,
            "year": int(_year[:4]),
            "month": int(_year[4:]) - 1,
            "value": float(_value)
        }
        values.append(value)
        months[value["month"]].append(value)

# sort months by value
for i in range(12):
    mlist = months[i]
    mlist = sorted(mlist, key=lambda m: -m["value"])
    for rank, m in enumerate(mlist):
        values[m["index"]]["rank"] = rank + 1

year_end = max([v['year'] for v in values])
yearCount = year_end - YEAR_START + 1
cellW = 1.0 * WIDTH / 12
cellH = 1.0 * HEIGHT / yearCount
maxValues = [-99] * 12

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2+YLABEL_WIDTH+WAVELENGTH_X, HEIGHT+PAD*2+XLABEL_HEIGHT+WAVELENGTH_Y), profile='full')

# x axis
dwgXAxis = dwg.add(dwg.g(id="xaxis"))
x = PAD + YLABEL_WIDTH + 0.5 * cellW
for m in range(12):
    oscy = mu.oscillate(1.0*m/11, WAVELENGTH_Y, FREQUENCY_Y)
    monthLabel = calendar.month_abbr[m+1]
    dwgXAxis.add(dwg.text(monthLabel, insert=(x, PAD+0.5*cellH+oscy), text_anchor="middle", alignment_baseline="middle", font_size=14))
    x += cellW

# y axis
dwgYAxis = dwg.add(dwg.g(id="yaxis"))
year = YEAR_START
y = PAD + XLABEL_HEIGHT + 0.5 * cellH
while year <= year_end:
    oscx = mu.oscillate(1.0*(year - YEAR_START)/yearCount, WAVELENGTH_X, FREQUENCY_X)
    dwgYAxis.add(dwg.text(str(year), insert=(PAD+0.5*YLABEL_WIDTH+oscx, y), text_anchor="middle", alignment_baseline="middle", font_size=14))
    y += cellH
    year += 1

# x grid
dwgXGrid = dwg.add(dwg.g(id="xgrid"))
for month in range(13):
    points = []
    xp = month % 11
    x = PAD + YLABEL_WIDTH + month * cellW
    oscy = mu.oscillate(1.0*xp/11, WAVELENGTH_Y, FREQUENCY_Y)
    for year in range(yearCount+1):
        yp = year % yearCount
        y = PAD + XLABEL_HEIGHT + year * cellH
        oscx = mu.oscillate(1.0*yp/yearCount, WAVELENGTH_X, FREQUENCY_X)
        points.append((x+oscx, y+oscy))
    dwgXGrid.add(dwg.polyline(points=points, stroke="#000000", stroke_width=2, fill="none"))

# y grid
# dwgYGrid = dwg.add(dwg.g(id="ygrid"))
# for year in range(yearCount+1):
#     points = []
#     y = PAD + XLABEL_HEIGHT + year * cellH
#     yp = year % yearCount
#     oscx = mu.oscillate(1.0*yp/yearCount, WAVELENGTH_X, FREQUENCY_X)
#     for month in range(13):
#         xp = month % 11
#         x = PAD + YLABEL_WIDTH + month * cellW
#         oscy = mu.oscillate(1.0*xp/11, WAVELENGTH_Y, FREQUENCY_Y)
#         points.append((x+oscx, y+oscy))
#     dwgYGrid.add(dwg.polyline(points=points, stroke="#000000", stroke_width=1, fill="none"))

# y grid
dwgYGrid = dwg.add(dwg.g(id="ygrid"))
for year in range(yearCount+1):
    points = []
    y = PAD + XLABEL_HEIGHT + year * cellH
    yp = year % yearCount
    oscx = mu.oscillate(1.0*yp/yearCount, WAVELENGTH_X, FREQUENCY_X)
    oscx2 = mu.oscillate(1.0*(yp-0.5)/yearCount, WAVELENGTH_X, FREQUENCY_X)
    for month in range(13):
        xp = month % 11
        x = PAD + YLABEL_WIDTH + month * cellW
        oscy = mu.oscillate(1.0*xp/11, WAVELENGTH_Y, FREQUENCY_Y)
        if month > 0:
            oscy2 = mu.oscillate(1.0*(xp-0.5)/11, WAVELENGTH_Y, FREQUENCY_Y)
            points.append((x+oscx-0.5*cellW, y+oscy2-EDGE))
        points.append((x+oscx, y+oscy))
    dwgYGrid.add(dwg.polyline(points=points, stroke="#000000", stroke_width=1, fill="none"))

# draw data
dwgLabels = dwg.add(dwg.g(id="labels"))
for i, v in enumerate(values):
    if v["year"] >= YEAR_START:
        x = v["month"] * cellW + PAD + YLABEL_WIDTH
        y = (v["year"] - YEAR_START) * cellH + PAD + XLABEL_HEIGHT
        cx = x + 0.5 * cellW
        cy = y + 0.5 * cellH
        label = "-"
        if v["rank"] <= MAX_RANK:
            label = str(v["rank"])

            oscx = mu.oscillate(1.0*(v["year"] - YEAR_START + 0.5)/yearCount, WAVELENGTH_X, FREQUENCY_X)
            oscy = mu.oscillate(1.0*(v["month"]+0.5)/11, WAVELENGTH_Y, FREQUENCY_Y)

            dwgLabels.add(dwg.text(label, insert=(cx+oscx, cy+oscy-EDGE*0.5), text_anchor="middle", alignment_baseline="middle", font_size=14))


dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
