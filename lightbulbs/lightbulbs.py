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
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-count', dest="COUNT", type=int, default=50, help="Lightbulbs per group")
parser.add_argument('-cols', dest="COLS", type=int, default=5, help="Columns")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/lightbulbs.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
COUNT = args.COUNT
COLS = args.COLS

# Data sources
# https://energy.gov/energysaver/how-energy-efficient-light-bulbs-compare-traditional-incandescents
# https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references#incanbulb
COST_PER_KWH = 0.11 # electricity rate of 11 cents per kilowatt-hour
HOURS_PER_DAY = 3.0 # average light bulb usage in hours per day
TREE_SEQUESTERED = 0.039 # 0.039 metric ton CO2 per urban tree seedling planted and grown for 10 years
lightbulbs = [
    {
        "id": "incandescent",
        "label": "Incandescent Bulbs",
        "annualEnergyCost": 4.8,
        "watts": 60,
        "lifeHours": 1000,
        "svg": "svg/bulb_inc.svg",
        "bulbCost": 1.53 # https://www.amazon.com/GE-Lighting-41028-60-Watt-4-Pack/dp/B01CTUERCU/ (1/29/2017)
    },{
        "id": "cfl",
        "label": "Compact Fluorescent Bulbs",
        "annualEnergyCost": 1.2,
        "lifeHours": 10000,
        "watts": 14,
        "svg": "svg/bulb_cfl.svg",
        "bulbCost": 2.2 # https://www.amazon.com/EcoSmart-5000K-Spiral-Daylight-4-Pack/dp/B0042UN1U0/ (1/29/2017)
    },{
        "id": "led",
        "label": "LED Bulbs",
        "annualEnergyCost": 1.0,
        "lifeHours": 25000,
        "watts": 8,
        "svg": "svg/bulb_led.svg",
        "bulbCost": 3.86 # https://www.amazon.com/Philips-459024-Equivalent-White-6-Pack/dp/B01439261O/ (1/29/2017)
    }
]

# Do energy/cost calculations
for i, l in enumerate(lightbulbs):
    energy = 1.0 * l["watts"] * HOURS_PER_DAY * 365 / 1000
    energyCost = energy * COST_PER_KWH
    lifeYears = 1.0 * l["lifeHours"] / 24 / 365
    bulbsPerYear = 1.0 / lifeYears
    bulbsCost = bulbsPerYear * l["bulbCost"]
    totalCost = bulbsCost + energyCost
    tonsCO2 = energy * 1671 / 1000 / 2204.6

    lightbulbs[i]["annualKwhConsumed"] = energy
    lightbulbs[i]["annualEnergyCost"] = energyCost
    lightbulbs[i]["annualBulbCost"] = bulbsCost
    lightbulbs[i]["annualTotalCost"] = totalCost
    lightbulbs[i]["annualCO2Emmissions"] = tonsCO2

# sort by cost and make the cheapest one the standard
newlist = sorted(lightbulbs, key=lambda k: k['annualTotalCost'])
standard = lightbulbs[-1].copy()

# do savings/reductions calculations
for i, l in enumerate(lightbulbs):
    costSavings = l["annualTotalCost"] - standard["annualTotalCost"]
    co2Reductions = l["annualCO2Emmissions"] - standard["annualCO2Emmissions"]
    treesPlanted = co2Reductions / TREE_SEQUESTERED

    lightbulbs[i]["annualSavingsIfReplaced"] = costSavings
    lightbulbs[i]["annualReductionsIfReplaced"] = co2Reductions
    lightbulbs[i]["treesPlantedEquivalent"] = treesPlanted

# print report
print "Annual light bulb stats:"
for l in lightbulbs:
    print "-----"
    print "%s:" % l["label"]
    print " - %skWh (%s metric tons CO2)" % (round(l["annualEnergyCost"], 2), round(l["annualCO2Emmissions"], 4))
    print " - $%s ($%s energy + $%s bulbs)" % (round(l["annualTotalCost"], 2), round(l["annualEnergyCost"], 2), round(l["annualBulbCost"], 2))
    if l["annualReductionsIfReplaced"] > 0:
        print " - $%s savings if switched to LED" % round(l["annualSavingsIfReplaced"], 2)
        print " - %s metric tons of CO2 reductions if switched to LED" % round(l["annualReductionsIfReplaced"], 4)
        print " - Equivalent to %s trees planted" % round(l["treesPlantedEquivalent"], 2)

# config svg
lightMargin = 0
groupMargin = 20
labelsHeight = 24
calculationHeight = 80
lightsHeight = HEIGHT - labelsHeight - calculationHeight

# init svg
rows = COUNT / COLS
dwg = svgwrite.Drawing(args.OUTPUT_FILE, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
dwgLabels = dwg.g(id="labels")

# definitions
for i, l in enumerate(lightbulbs):
    group = dwg.g(id=l["id"])
    svgData = svgu.getDataFromSVG(l["svg"])
    lightbulbs[i]["svgData"] = svgData
    for path in svgData["paths"]:
        group.add(dwg.path(d=path, fill="#000000"))
    dwg.defs.add(group)

# draw lightbulbs
xOffset = PAD
groupW = 1.0 * (WIDTH - groupMargin * (len(lightbulbs) - 1)) / len(lightbulbs)
lightW = 1.0 * (groupW - lightMargin * (COLS - 1)) / COLS
lightH = 1.0 * lightsHeight / rows - lightMargin
for l in lightbulbs:
    scaleW = lightW / l["svgData"]["width"]
    scaleH = lightH / l["svgData"]["height"]
    scale = scaleW
    dwgLightgroup = dwg.g()
    y = PAD
    # draw labels
    xc = xOffset + 0.5 * (lightW * COLS + lightMargin * (COLS-1))
    dwgLabels.add(dwg.text(l["label"], insert=(xc, y), text_anchor="middle", alignment_baseline="before-edge", font_size=14))
    y += labelsHeight
    for row in range(rows):
        x = xOffset
        for col in range(COLS):
            dwgLightgroup.add(dwg.use("#"+l["id"], transform="translate(%s, %s) scale(%s)" % (x, y, scale)))
            x += lightW + lightMargin
        y += lightH + lightMargin
    xOffset += groupW + groupMargin
    dwg.add(dwgLightgroup)

# multiplication
mw = 5
mh = 20
mc = mh * 0.5
mm = mc - mw * 0.5
xGroup = dwg.g(id="multiply", transform="rotate(45, %s, %s)" % (mc, mc))
xGroup.add(dwg.rect(insert=(mm, 0), size=(mw, mh), fill="#000000"))
xGroup.add(dwg.rect(insert=(0, mm), size=(mh, mw), fill="#000000"))
dwg.defs.add(xGroup)

# equal
eOffset = 3
eGroup = dwg.g(id="equals")
eGroup.add(dwg.rect(insert=(0, eOffset), size=(mh, mw), fill="#000000"))
eGroup.add(dwg.rect(insert=(0, mh-mw-eOffset), size=(mh, mw), fill="#000000"))
dwg.defs.add(eGroup)

# draw calculations
dwgCalc = dwg.g(id="calculations")
xOffset = PAD
yOffset = PAD + labelsHeight + lightsHeight + 15
for l in lightbulbs:
    savings = int(round(l["annualSavingsIfReplaced"]))
    if savings <= 0:
        continue
    y = yOffset
    x = xOffset
    dwgCalc.add(dwg.use("#multiply", transform="translate(%s, %s)" % (x, y)))
    dwgLabels.add(dwg.text("$%s" % savings, insert=(x+40, y), font_weight="bold", font_size=36, alignment_baseline="mathematical"))
    y += 30
    dwgCalc.add(dwg.rect(insert=(x, y), size=(groupW, 5)))
    y += 16
    dwgCalc.add(dwg.use("#equals", transform="translate(%s, %s)" % (x, y)))
    xOffset += groupW + groupMargin
dwg.add(dwgCalc)

dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))

dwg.add(dwgLabels)
dwg.save()
print "Saved svg: %s" % args.OUTPUT_FILE
