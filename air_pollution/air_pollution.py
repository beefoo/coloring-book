# -*- coding: utf-8 -*-

# Usage:
#   python air_pollution.py
#   python air_pollution.py -input data/delhi_openaq_formatted.csv -color True -output data/air_pollution_delhi_color.svg

import argparse
import base64
import csv
import datetime
import glob
import inspect
import math
import matplotlib.pyplot as plt
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
# input source: http://www.stateair.net/web/historical/1/1.html
parser.add_argument('-input', dest="INPUT_FILE", default="data/Beijing_2015_HourlyPM25_created20160201.csv", help="Path to input file")
parser.add_argument('-reduce', dest="REDUCE", default="max", help="How to reduce a day of data: max or mean")
parser.add_argument('-dpr', dest="DAYS_PER_ROW", type=int, default=20, help="Amount of days to display per row")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-osc', dest="OSCILLATE", type=float, default=24.0, help="Amount to oscillate")
parser.add_argument('-daypad', dest="DAY_PAD", type=int, default=0, help="Padding around each day")
parser.add_argument('-rowpad', dest="ROW_PAD", type=int, default=6, help="Padding around each row")
parser.add_argument('-color', dest="SHOW_COLOR", type=bool, default=False, help="Whether or not to display color")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/Beijing_2015_DailyPM25.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
OSCILLATE = args.OSCILLATE
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2 - OSCILLATE * 2
DAYS_PER_ROW = args.DAYS_PER_ROW
DAY_PAD = args.DAY_PAD
ROW_PAD = args.ROW_PAD
SHOW_COLOR = args.SHOW_COLOR

# Config Air Quality Index
# https://www.airnow.gov/index.cfm?action=aqibasics.aqi
# http://ec.europa.eu/environment/integration/research/newsalert/pdf/24si_en.pdf
AQI = [
    {"max": 50, "label": "Good", "color": "Green", "meaning": "Air quality is considered satisfactory, and air pollution poses little or no risk.", "image": "data/lime.png"},
    {"max": 100, "label": "Moderate", "color": "Yellow", "meaning": "Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution.", "image": "data/yellow.png"},
    {"max": 150, "label": "Unhealthy for Sensitive Groups", "color": "Orange", "meaning": "Members of sensitive groups may experience health effects. The general public is not likely to be affected.", "image": "data/orange.png"},
    {"max": 200, "label": "Unhealthy", "color": "Red", "meaning": "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.", "image": "data/red.png"},
    {"max": 300, "label": "Very Unhealthy", "color": "Purple", "meaning": "Health alert: everyone may experience more serious health effects.", "image": "data/violet.png"},
    {"max": 500, "label": "Hazardous", "color": "Maroon", "meaning": "Health warnings of emergency conditions. The entire population is more likely to be affected.", "image": "data/brown.png"},
    {"max": 9999, "label": "Beyond Index", "color": "Black", "meaning": "Air quality is so bad it exceeds the maximum defined value on the Air Quality Index.", "image": "data/black.png"}
]

def dayOfWeek(date):
    # make sunday the first day of the week
    weekday = date.weekday() + 1
    if weekday > 6:
        weekday = 0
    return weekday

def reduceData(data):
    if args.REDUCE == "max":
        return max(data)
    else:
        return mu.mean(data)

def getValue(value, index):
    v = len(index)
    for i, r in enumerate(index):
        if value < r["max"]:
            v = i + 1
            break
    return v

def getGroup(value, index):
    group = index[-1]
    for r in index:
        if value < r["max"]:
            group = r
            break
    return group

# Read file
readings = []
with open(args.INPUT_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    current_date = None
    queue = []
    # remove intro lines and header
    for skip in range(4):
        next(r, None)
    # for each row
    currentMonth = -1
    sort = 0
    for _site,_parameter,_date,_year,_month,_day,_hour,_value,_unit,_duration,_qc in r:
        value = int(round(float(_value)))
        date = datetime.date(int(_year), int(_month), int(_day))
        sort = 10000*int(_year) + 100*int(_month) + int(_day)
        if currentMonth != date.month:
            readings.append({
                'date': date,
                'label': date.strftime("%b"),
                'sort': sort - 0.1
            })
            currentMonth = date.month
        if value >= 0:
            if current_date is None:
                current_date = date
                queue.append(value)
            elif current_date != date:
                readings.append({
                    'date': current_date,
                    'value': reduceData(queue),
                    'sort': sort
                })
                queue = []
                current_date = date
            else:
                queue.append(value)
    if len(queue) > 0:
        readings.append({
            'date': current_date,
            'value': reduceData(queue),
            'sort': sort
        })

# sort chronologically
readings = sorted(readings, key=lambda k: k['sort'])

# Show a chart
# y = [r['value'] for r in readings]
# x = range(len(y))
# width = 1/1.5
# plt.bar(x, y, width, color="blue")
# plt.show()

# init svg
offsetDaysPerRow = DAYS_PER_ROW + 0.5
rows = int(math.ceil(1.0 * len(readings) / DAYS_PER_ROW))
cell_w = 1.0 * WIDTH / offsetDaysPerRow
cell_h = 1.0 * (HEIGHT - ROW_PAD * (rows-1)) / rows
cell_l = min(cell_w, cell_h)
xOffset = (WIDTH - (cell_l * offsetDaysPerRow)) * 0.5
yOffset = (HEIGHT - (cell_l * rows) - ROW_PAD * (rows-1)) * 0.5
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2+OSCILLATE*2), profile='full')

# define color patterns
if SHOW_COLOR:
    for g in AQI:
        imageSize = (300, 300)
        imageData = ""
        with open(g["image"], "rb") as f:
            imageData = base64.b64encode(f.read())
        dwgImage = dwg.image(href="data:image/png;base64,%s" % imageData, insert=(0, 0), size=imageSize)
        dwgPattern = dwg.pattern(id="pattern%s" % g["max"], patternUnits="userSpaceOnUse", size=imageSize)
        dwgPattern.add(dwgImage)
        dwg.defs.add(dwgPattern)

# add days to svg
day_r = (cell_l - DAY_PAD * 2) * 0.5
dwgShapes = dwg.add(dwg.g(id="shapes"))
dwgLabels = dwg.add(dwg.g(id="labels"))
dwgMonths = dwg.add(dwg.g(id="months"))
arrow = []
for i, r in enumerate(readings):
    row = int(i / DAYS_PER_ROW)
    col = i % DAYS_PER_ROW
    rowOffset = row * ROW_PAD
    x = col * cell_l + cell_l * 0.5 + PAD + xOffset
    o = 1.0*col/DAYS_PER_ROW
    if row % 2 > 0:
        x += cell_l * 0.5
        o = 1.0*(col+0.5)/DAYS_PER_ROW
    osc = mu.oscillate(o, OSCILLATE)
    y = row * cell_l + cell_l * 0.5 + PAD + OSCILLATE + osc + yOffset + rowOffset
    # add arrow point
    if i > 0 and i < 6:
        arrow.append((x, y - cell_l))
    # add month label
    if "label" in r:
        x += cell_l * 0.1
        dwgMonths.add(dwg.text(r["label"], insert=(x, y), text_anchor="middle", alignment_baseline="middle", font_size=12))
    else:
        color = "none"
        if SHOW_COLOR:
            group = getGroup(r['value'], AQI)
            color = "url(#pattern%s)" % group["max"]
        # add circle
        dwgShapes.add(dwg.circle(center=(x, y), r=day_r, stroke="#000000", stroke_width=2, fill=color))
        # add value as label
        value = getValue(r['value'], AQI)
        dwgLabels.add(dwg.text(str(value), insert=(x, y), text_anchor="middle", alignment_baseline="middle", font_size=12))

# add arrow
dwgArrow = dwg.add(dwg.g(id="arrow"))
arrowPath = svgu.pointsToCurve(arrow)
dwgArrow.add(dwg.path(d=arrowPath, stroke="#000000", stroke_width=3, fill="none"))
arrowHeadH = 10
d = arrowHeadH
r = d * 0.5
p = arrow[-1]
arrowHead = [
    (p[0], p[1]-r),
    (p[0] + d, p[1]),
    (p[0], p[1]+r),
]
dwgArrow.add(dwg.polygon(points=arrowHead, fill="#000000"))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
