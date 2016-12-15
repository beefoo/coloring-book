# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import glob
import math
import matplotlib.pyplot as plt
import os
import svgwrite
from svgwrite import inch, px

# input
parser = argparse.ArgumentParser()
# input source: http://www.stateair.net/web/historical/1/1.html
parser.add_argument('-input', dest="INPUT_FILE", default="data/Beijing_2015_HourlyPM25_created20160201.csv", help="Path to input file")
parser.add_argument('-reduce', dest="REDUCE", default="max", help="How to reduce a day of data: max or mean")
parser.add_argument('-wpr', dest="WEEKS_PER_ROW", type=int, default=2, help="Amount of weeks to display per row")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-daypad', dest="DAY_PAD", type=int, default=2, help="Padding around each day")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/Beijing_2015_DailyPM25.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WEEKS_PER_ROW = args.WEEKS_PER_ROW
WIDTH = args.WIDTH
PAD = args.PAD
DAY_PAD = args.DAY_PAD

# Config Air Quality Index
# https://www.airnow.gov/index.cfm?action=aqibasics.aqi
AQI = [
    {"max": 50, "label": "Good", "color": "Green", "meaning": "Air quality is considered satisfactory, and air pollution poses little or no risk."},
    {"max": 100, "label": "Moderate", "color": "Yellow", "meaning": "Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution."},
    {"max": 150, "label": "Unhealthy for Sensitive Groups", "color": "Orange", "meaning": "Members of sensitive groups may experience health effects. The general public is not likely to be affected."},
    {"max": 200, "label": "Unhealthy", "color": "Red", "meaning": "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects."},
    {"max": 300, "label": "Very Unhealthy", "color": "Purple", "meaning": "Health alert: everyone may experience more serious health effects."},
    {"max": 500, "label": "Hazardous", "color": "Maroon", "meaning": "Health warnings of emergency conditions. The entire population is more likely to be affected."},
    {"max": 9999, "label": "Beyond Index", "color": "Black", "meaning": "Air quality is so bad it exceeds the maximum defined value on the Air Quality Index."}
]

def dayOfWeek(date):
    # make sunday the first day of the week
    weekday = date.weekday() + 1
    if weekday > 6:
        weekday = 0
    return weekday

# Mean of list
def mean(data):
    n = len(data)
    if n < 1:
        return 0
    else:
        return sum(data) / n

def reduceData(data):
    if args.REDUCE == "max":
        return max(data)
    else:
        return mean(data)

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
    for _site,_parameter,_date,_year,_month,_day,_hour,_value,_unit,_duration,_qc in r:
        value = int(_value)
        date = datetime.date(int(_year), int(_month), int(_day))
        if value >= 0:
            if current_date is None:
                current_date = date
                queue.append(value)
            elif current_date != date:
                readings.append({
                    'date': current_date,
                    'value': reduceData(queue)
                })
                queue = []
                current_date = date
            else:
                queue.append(value)
    if len(queue) > 0:
        readings.append({
            'date': current_date,
            'value': reduceData(queue)
        })

# sort chronologically
readings = sorted(readings, key=lambda k: k['date'])

# Show a chart
# y = [r['value'] for r in readings]
# x = range(len(y))
# width = 1/1.5
# plt.bar(x, y, width, color="blue")
# plt.show()

# init svg
offset = dayOfWeek(readings[0]['date'])
days_per_row = WEEKS_PER_ROW * 7
rows = math.ceil((365.0 + offset) / days_per_row)
cell_w = 1.0 * WIDTH / days_per_row
cell_h = cell_w
height = cell_h * rows
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=((WIDTH+PAD*2)*px, (height+PAD*2)*px), profile='full')

# add days to svg
day_r = (cell_w - DAY_PAD * 2) * 0.5
dwgShapes = dwg.add(dwg.g(id="shapes"))
dwgLabels = dwg.add(dwg.g(id="labels"))
# dwgMonths = dwg.add(dwg.g(id="months"))
# currentMonth = ""
for i, r in enumerate(readings):
    weekday = dayOfWeek(r['date'])
    j = i + offset
    week = int((i + offset) / 7)
    row = int((i + offset) / days_per_row)
    col = 7 * (week % WEEKS_PER_ROW) + weekday
    x = col * cell_w + cell_w * 0.5 + PAD
    y = row * cell_h + cell_h * 0.5 + PAD
    # add circle
    dwgShapes.add(dwg.circle(center=(x, y), r=day_r, stroke="#000000", stroke_width=2, fill="none"))
    # add value as label
    dwgLabels.add(dwg.text(str(r['value']), insert=(x, y), text_anchor="middle", alignment_baseline="middle", font_size=10))
    # add month label
    # month = r['date'].strftime("%b")
    # if currentMonth != month:
    #     dwgMonths.add(dwg.text(month, insert=(x-day_r, y-day_r), text_anchor="middle", alignment_baseline="middle", font_size=10))
    #     currentMonth = month

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
