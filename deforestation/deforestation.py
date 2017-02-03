# -*- coding: utf-8 -*-

import argparse
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
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/deforestation.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

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

fieldRatioW = 4.0
fieldRatioH = 3.0
degreesPerField = 360.0 / lossFFPerMinute

# get field W/H given radius
pageRadius = min(WIDTH, HEIGHT) * 0.5
radius = pageRadius * 0.7
fieldH = 2.0 * radius * math.cos(math.radians(0.5*(180-degreesPerField)))
fieldW = fieldH * (fieldRatioW / fieldRatioH)
# print "%s, %s, %s" % (fieldW, fieldH, radius)
# sys.exit(1)

# init svg
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
# dwg.add(dwg.line(start=(PAD, 0), end=(PAD, HEIGHT+PAD*2), stroke="#000000"))

# field reference
fieldStrokeW = 1.5
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

# draw fields
angle = -90 - 0.5 * degreesPerField
cx = WIDTH * 0.5 + PAD
cy = HEIGHT * 0.5 + PAD
dwgFields = dwg.add(dwg.g(id="fields"))
dwgLabels = dwg.add(dwg.g(id="labels"))
for i in range(lossFFPerMinute):
    (x, y) = mu.translatePoint((cx, cy), math.radians(angle), radius)
    rotate = angle + 0.5 * degreesPerField
    dwgFields.add(dwg.use("#field", transform="translate(%s,%s) rotate(%s)" % (x, y, rotate)))
    if int(rotate) % 90 == 0:
        label = "60"
        d = (int(rotate) + 90) / 90
        if d > 0:
            label = str(d * 15)
        labelP = mu.translatePoint((cx, cy), math.radians(rotate), radius*0.86)
        dwgLabels.add(dwg.text(label, insert=labelP, text_anchor="middle", alignment_baseline="middle", font_size=24))
    angle += degreesPerField

# draw clock hands
dwgClock = dwg.add(dwg.g(id="clock"))
handR = 5
handL = radius * 0.667
handPath = [
    "M%s,%s" % (cx, cy - handL),
    "L%s,%s" % (cx + handR, cy),
    "Q%s,%s %s,%s" % (cx, cy + handR*1.5, cx - handR, cy),
    "Z"
]
dwgClock.add(dwg.path(d=handPath, stroke="#000000", fill="none", stroke_width=2))

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
