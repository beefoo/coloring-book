# -*- coding: utf-8 -*-

import argparse
import inspect
import math
import os
import random
import re
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.svgutils as svgu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-row', dest="PER_ROW", type=int, default=8, help="Columns")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/lightbulbs.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD
PER_ROW = args.PER_ROW

# 2.82 x 10-2 metric tons CO2 / bulb replaced
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#incanbulb
LIGHTBULB_REDUCTIONS = 0.0282

# 40 lightbulbs per U.S. household
# https://www.energystar.gov/ia/partners/manuf_res/CFL_PRG_FINAL.pdf
LIGHTBULBS_PER_HOUSEHOLD = 40

# 0.039 metric ton CO2 per urban tree seedling planted and grown for 10 years
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#seedlings
TREE_SEQUESTERED = 0.039

# $4.80 annual cost per incandescent lightbulb
# Based on 2 hrs/day of usage, an electricity rate of 11 cents per kilowatt-hour, shown in U.S. dollars.
# Lasts ~1000 hours
# https://energy.gov/energysaver/how-energy-efficient-light-bulbs-compare-traditional-incandescents
INCANDESCENT_COST = 4.8

# $1.00 annual cost per LED lightbulb
# https://energy.gov/energysaver/how-energy-efficient-light-bulbs-compare-traditional-incandescents
# Lasts ~25,000 hours
LED_COST = 1.0

householdReductions = LIGHTBULB_REDUCTIONS * LIGHTBULBS_PER_HOUSEHOLD
treeEquivalent = int(round(householdReductions / TREE_SEQUESTERED))

print "Replacing lightbulbs in one household is equivelent to planting %s urban tree seedlings and letting grow for 10 years" % treeEquivalent

beforeSavings = int(round(INCANDESCENT_COST * LIGHTBULBS_PER_HOUSEHOLD))
afterSavings = int(round(LED_COST * LIGHTBULBS_PER_HOUSEHOLD))
savings = int(round(beforeSavings - afterSavings))
print "Replacing lightbulbs in one household will save about $%s ($%s vs $%s)" % (savings, beforeSavings, afterSavings)

# config svg
svgMargin = 10
svgData = svgu.getDataFromSVG("svg/dollar_02.svg")
svgWidth = (1.0 * WIDTH - 1.0 * svgMargin * (PER_ROW-1)) / PER_ROW
svgHeight = svgWidth * svgData["height"] / svgData["width"]
rows = math.ceil(1.0 * beforeSavings / PER_ROW)
scale = svgWidth / svgData["width"]

# init svg
height = rows * (svgHeight + svgMargin) - svgMargin
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, height+PAD*2), profile='full')

# make reference dollar
dollarGroup = dwg.g(id="dollar")
for path in svgData["paths"]:
    dollarGroup.add(dwg.path(d=path, fill="none", stroke="#000000", stroke_width=1))
dwg.defs.add(dollarGroup)

for i in range(beforeSavings):
    row = i / PER_ROW
    col = i % PER_ROW
    x = col * (svgWidth + svgMargin) + PAD
    y = row * (svgHeight + svgMargin) + PAD
    group = dwg.g(transform="translate(%s, %s) scale(%s)" % (x, y, scale))
    group.add(dwg.use("#dollar"))
    dwg.add(group)

dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
