# -*- coding: utf-8 -*-

import argparse
import csv
import svgwrite

# input
parser = argparse.ArgumentParser()
# input source: http://www.stateair.net/web/historical/1/1.html
parser.add_argument('-input', dest="INPUT_FILE", default="data/188001-201610_land_ocean.csv", help="Path to input file")
parser.add_argument('-ys', dest="YEAR_START", type=int, default=1986, help="Year start on viz")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=int, default=1200, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-osc', dest="OSCILLATE", type=float, default=40.0, help="Amount to oscillate")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/188001-201610_land_ocean.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT
YEAR_START = args.YEAR_START
PAD = args.PAD
OSCILLATE = args.OSCILLATE

values = []

# read csv
with open(args.INPUT_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    for skip in range(4):
        next(r, None)
    # for each row
    for _year,_value in r:
        values.append({
            "key": _year,
            "year": int(_year[:4]),
            "month": int(_year[4:]) - 1,
            "value": float(_value)
        })

year_end = max([v['year'] for v in values])
yearCount = year_end - YEAR_START + 1
cellW = 1.0 * WIDTH / 12
cellH = 1.0 * HEIGHT / yearCount
maxValues = [-99] * 12

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgLabels = dwg.add(dwg.g(id="labels"))

for i, v in enumerate(values):
    record = False
    month = v["month"]
    value = v["value"]
    if value >= maxValues[month]:
        record = True
        maxValues[month] = value
    if v["year"] >= YEAR_START:
        x = month * cellW
        y = (v["year"] - YEAR_START) * cellH
        cx = x + 0.5 * cellW
        cy = y + 0.5 * cellH
        label = '-'
        if record:
            label = 'R'
        dwgLabels.add(dwg.text(label, insert=(cx, cy), text_anchor="middle", alignment_baseline="middle", font_size=14))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
