# -*- coding: utf-8 -*-

import argparse
import csv
import math
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/re_actual_potential.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2
CIRCLE_MARGIN = 10

# conversion between BTU and Watt Hour
BTU_PER_WH = 3.412141633
WH_PER_BTU = 1.0 / BTU_PER_WH

# Total energy consumption / U.S. / 2015 / Trillion Btu:
# http://www.eia.gov/totalenergy/data/annual/
totalEnergyConsumption = 0
YYYYMM = "201613"
MSN = "TETCBUS"
filename = "data/energy_consumption_2016.csv"
with open(filename, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    next(r, None)
    for _MSN, _YYYYMM, _Value, _Column_Order, _Description, _Unit in r:
        if _YYYYMM == YYYYMM and _MSN == MSN:
            # Given in Quadrillion Btu / convert to Trillion Btu
            totalEnergyConsumption = float(_Value) * 1000
            break
if totalEnergyConsumption <= 0:
    print "Total energy consumption not found."
    sys.exit(1)
print "Total energy consumption: %s" % totalEnergyConsumption

# Renewable energy production / U.S. / 2015 / Trillion Btu:
# http://www.eia.gov/totalenergy/data/annual/
totalREProduction = 0
YYYYMM = "201613"
MSN = "REPRBUS"
filename = "data/energy_production_2016.csv"
with open(filename, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    next(r, None)
    for _MSN, _YYYYMM, _Value, _Column_Order, _Description, _Unit in r:
        if _YYYYMM == YYYYMM and _MSN == MSN:
            # Given in Quadrillion Btu / convert to Trillion Btu
            totalREProduction = float(_Value) * 1000
            break
if totalREProduction <= 0:
    print "RE production not found."
    sys.exit(1)
print "Total RE production: %s (%s%%)" % (totalREProduction, round(1.0*totalREProduction/totalEnergyConsumption*100, 2))

# Wind/solar potential / U.S. / 2012 / Terawatt Hours:
# http://www.nrel.gov/gis/re_potential.html
rePotential = 0
solarPotential = 0
solarKeys = ["Urban utility-scale PV", "Rural utility-scale PV", "Rooftop PV", "Concentrating solar power"]
filename = "data/re_technical_potential_summary.csv"
dp = {}
with open(filename, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    next(r, None)
    for _Technology, _Generation_Potential_Twh, _Capacity_Potential_GW in r:
        # convert twh to trillion btu
        rePotential += float(_Generation_Potential_Twh) * BTU_PER_WH
        if _Technology in solarKeys:
            solarPotential += float(_Generation_Potential_Twh) * BTU_PER_WH
print "RE potential: %s (%s%%)" % (rePotential,  round(1.0*rePotential/totalEnergyConsumption*100, 1))
print "Solar potential: %s (%s%%)" % (solarPotential,  round(1.0*solarPotential/totalEnergyConsumption*100, 1))

def writeSvg(filename, data):
    # sort data
    data = sorted(data, key=lambda k: k['value'])

    # init svg
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')

    # make patterns
    # diagonalPattern = dwg.pattern(id="diagonal", patternUnits="userSpaceOnUse", size=(20,20))
    # diagonalPattern.add(dwg.rect(insert=(0,0), size=(20,20), fill="#FFFFFF"))
    # diagonalPattern.add(dwg.path(d="M 0,20 l 20,-20 M -5,5 l 10,-10 M 15,25 l 10,-10", stroke_width=1, stroke="#000000"))
    # dwg.defs.add(diagonalPattern)
    scale = 0.667
    stroke = 1.0 / 0.5
    honeycombPattern = dwg.pattern(id="honeycomb", patternUnits="userSpaceOnUse", size=(56,100), patternTransform="scale(%s)" % scale)
    honeycombPattern.add(dwg.rect(insert=(0,0), size=(56,100), fill="#FFFFFF"))
    honeycombPattern.add(dwg.path(d="M28 66L0 50L0 16L28 0L56 16L56 50L28 66L28 100", fill="none", stroke="#000000", stroke_width=stroke))
    honeycombPattern.add(dwg.path(d="M28 0L28 34L0 50L0 84L28 100L56 84L56 50L28 34", fill="none", stroke="#000000", stroke_width=stroke))
    dwg.defs.add(honeycombPattern)
    circleSize = 12
    circlesPattern = dwg.pattern(id="circles", patternUnits="userSpaceOnUse", size=(circleSize,circleSize))
    circlesPattern.add(dwg.rect(insert=(0,0), size=(circleSize,circleSize), fill="#FFFFFF"))
    circlesPattern.add(dwg.circle(center=(circleSize/2,circleSize/2), r=1, fill="#000000"))
    circlesPattern.add(dwg.circle(center=(0,0), r=1, fill="#000000"))
    circlesPattern.add(dwg.circle(center=(0,circleSize), r=1, fill="#000000"))
    circlesPattern.add(dwg.circle(center=(circleSize,0), r=1, fill="#000000"))
    circlesPattern.add(dwg.circle(center=(circleSize,circleSize), r=1, fill="#000000"))
    dwg.defs.add(circlesPattern)
    # wavesPattern = dwg.pattern(id="waves", patternUnits="userSpaceOnUse", size=(20,20))
    # wavesPattern.add(dwg.rect(insert=(0,0), size=(20,20), fill="#FFFFFF"))
    # wavesPattern.add(dwg.path(d="M0 10 c 2.5 -5 , 7.5 -5 , 10 0 c 2.5 5 , 7.5 5 , 10 0 M -10 10 c 2.5 5 , 7.5 5 , 10 0 M 20 10 c 2.5 -5 , 7.5 -5 , 10 0", stroke_width=1, stroke="#000000", stroke_linecap="square", fill="none"))
    wavesPattern = dwg.pattern(id="waves", patternUnits="userSpaceOnUse", size=(48,32), patternTransform="scale(0.75) rotate(45)")
    wavesPattern.add(dwg.rect(insert=(0,0), size=(48,32), fill="#FFFFFF"))
    wavesPattern.add(dwg.path(d="M27 32c0-3.314 2.686-6 6-6 5.523 0 10-4.477 10-10S38.523 6 33 6c-3.314 0-6-2.686-6-6h2c0 2.21 1.79 4 4 4 6.627 0 12 5.373 12 12s-5.373 12-12 12c-2.21 0-4 1.79-4 4h-2zm-6 0c0-3.314-2.686-6-6-6-5.523 0-10-4.477-10-10S9.477 6 15 6c3.314 0 6-2.686 6-6h-2c0 2.21-1.79 4-4 4C8.373 4 3 9.373 3 16s5.373 12 12 12c2.21 0 4 1.79 4 4h2z", fill="#000000"))
    dwg.defs.add(wavesPattern)

    # calculate radius
    totalHeight = 1.0 * HEIGHT - CIRCLE_MARGIN * (len(data)-1)
    diameter = totalHeight / (sum([math.sqrt(d["value"]) for d in data]))
    radius = diameter * 0.5
    area = math.pi * math.pow(radius, 2)

    y = 0
    shapes = dwg.add(dwg.g(id="shapes"))
    for i, item in enumerate(data):
        itemArea = area * item["value"]
        itemRadius = math.sqrt(itemArea / math.pi)
        y += itemRadius
        x = WIDTH*0.5
        shapes.add(dwg.circle(center=(x+PAD, y+PAD), r=itemRadius, fill="url(#%s)" % item["pattern"], stroke="#000000", stroke_width=item["width"]))
        y += itemRadius + CIRCLE_MARGIN
    dwg.add(dwg.rect(insert=(PAD,PAD), size=(WIDTH, HEIGHT), stroke_width=1, stroke="#000000", fill="none"))
    dwg.save()
    print "Saved svg: %s" % filename

actualRenewable = totalREProduction
potentialRenewable = rePotential
maxValue = max([totalEnergyConsumption, actualRenewable, potentialRenewable])
writeSvg(args.OUTPUT_FILE, [
    {"label": "Total energy consumption", "value": totalEnergyConsumption / maxValue, "width": 3, "pattern": "waves"},
    {"label": "Renewable energy production", "value": actualRenewable / maxValue, "width": 3, "pattern": "circles"},
    {"label": "Renewable energy potential", "value": potentialRenewable / maxValue, "width": 3, "pattern": "honeycomb"}
])
