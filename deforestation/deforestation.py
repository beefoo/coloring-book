# -*- coding: utf-8 -*-

import argparse
import math
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.25, help="Padding of output file")
parser.add_argument('-row', dest="PER_ROW", type=int, default=3, help="Fields per row")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/deforestation.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 150
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
PER_ROW = args.PER_ROW

# source: http://www.fao.org/3/a-i4793e.pdf
# 1990: million hectares of forest globally
START_MHA = 4128
# 2015: million hectares of forest globally
END_MHA = 3999
LOSS_MHA = START_MHA - END_MHA

# football field in square meters (100m x 50m)
ffM2 = 5000

# hectares in square meters
haM2 = 10000

# football fields per hectare
ffPerHa = haM2 / ffM2

# hectare loss
years = 2015 - 1990
lossMhaPerYear = 1.0 * LOSS_MHA / years
lossHaPerDay = lossMhaPerYear / 365.25 * 1000000
lossHaPerHour = lossHaPerDay / 24
lossHaPerMinute = lossHaPerHour / 60
lossFFPerMinute = int(round(lossHaPerMinute * ffPerHa))

print "Net global forest loss per minute: %s football fields" % lossFFPerMinute

# init svg
rows = int(math.ceil(1.0 * lossFFPerMinute / PER_ROW))
fieldW = 1.0 * WIDTH / PER_ROW
fieldH = fieldW * 0.75
height = fieldH * rows
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2+fieldW*0.5, height+PAD*2), profile='full')

# field reference

fieldStrokeW = 2
goalH = fieldH * 0.5
goalW = fieldW * 0.2
goalY = (fieldH - goalH) * 0.5
dwgField = dwg.g(id="field")
dwgField.add(dwg.rect(insert=(0,0), size=(fieldW, fieldH), stroke_width=(fieldStrokeW*2), stroke="#000000", fill="none")) # outline
dwgField.add(dwg.line(start=(fieldW*0.5, 0), end=(fieldW*0.5, fieldH), stroke_width=fieldStrokeW, stroke="#000000")) # half line
dwgField.add(dwg.circle(center=(fieldW*0.5, fieldH*0.5), r=fieldH*0.15, stroke_width=fieldStrokeW, stroke="#000000", fill="none")) # center circle
dwgField.add(dwg.rect(insert=(0,goalY), size=(goalW, goalH), stroke_width=fieldStrokeW, stroke="#000000", fill="none")) # left goal
dwgField.add(dwg.rect(insert=(fieldW-goalW,goalY), size=(goalW, goalH), stroke_width=fieldStrokeW, stroke="#000000", fill="none")) # right goal
dwg.defs.add(dwgField)

halfFieldW = fieldW * 0.5
halfFieldH = fieldH * 0.5
direction = 1
scale = 0.85
y = 0
for row in range(rows):
    x = 0
    offsetx = row % 2 * halfFieldW
    for col in range(PER_ROW):
        i = row * PER_ROW + col
        # add offset for uneven row
        if col <= 0 and offsetx <= 0 and (lossFFPerMinute-i) < PER_ROW:
            x += fieldW
        if i >= lossFFPerMinute:
            break
        t = "translate(%s,%s) scale(%s) rotate(%s %s %s)" % (PAD+x+offsetx, PAD+y, scale, 45*direction, halfFieldW, halfFieldH)
        g = dwg.add(dwg.g(id="field%s" % i, transform=t))
        g.add(dwg.use("#field"))
        x += fieldW
    y += fieldH * scale
    direction *= -1

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
