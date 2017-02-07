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

# conversion between BTU and Watt Hour
BTU_PER_WH = 3.412141633
WH_PER_BTU = 1.0 / BTU_PER_WH

# Total energy consumption / U.S. / 2015 / Trillion Btu:
# http://www.eia.gov/totalenergy/data/annual/
totalEnergyConsumption = 0
YYYYMM = "201513"
filename = "data/energy_consumption.csv"
with open(filename, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    next(r, None)
    for _MSN, _YYYYMM, _Value, _Column_Order, _Description, _Unit in r:
        if _YYYYMM == YYYYMM:
            # Given in Quadrillion Btu / convert to Trillion Btu
            totalEnergyConsumption = float(_Value) * 1000
            break
if totalEnergyConsumption <= 0:
    print "Total energy consumption not found."
    sys.exit(1)
print "Total energy consumption: %s" % totalEnergyConsumption

# Wind production / U.S. / 2015 / Terawatt Hours:
# https://www.eia.gov/renewable/data.cfm#wind
windProduction = 0
year = "2015"
filename = "data/energy_production_wind.csv"
with open(filename, 'rb') as f:
    for skip in range(5):
        next(f, None)
    r = csv.reader(f, delimiter=',')
    for _Year, _All, _Iowa, _Texas in r:
        if year == _Year:
            # Given in Gigawatt hours; convert to Tera
            windProduction = float(_All) / 1000.0
            break
if windProduction <= 0:
    print "Wind production not found."
    sys.exit(1)
print "Total wind production: %s (%s:1)" % (windProduction, int(round(totalEnergyConsumption/windProduction)))

# Solar production / U.S. / 2015 / Terawatt Hours:
# https://www.eia.gov/renewable/data.cfm#summary
solarProduction = 0
YYYYMM = "201513"
filename = "data/energy_production_solar.csv"
with open(filename, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    next(r, None)
    for _MSN, _YYYYMM, _Value, _Column_Order, _Description, _Unit in r:
        if YYYYMM == _YYYYMM:
            # Given in Gigawatt hours; convert to Tera
            solarProduction = float(_Value) / 1000.0
            break
if solarProduction <= 0:
    print "Solar production not found."
    sys.exit(1)
print "Total solar production: %s (%s:1)" % (solarProduction, int(round(totalEnergyConsumption/solarProduction)))

# Wind/solar potential / U.S. / 2012 / Terawatt Hours:
# http://www.nrel.gov/gis/re_potential.html
windPotential = 0
solarPotential = 0
filename = "data/re_technical_potential_summary.csv"
dp = {}
with open(filename, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    next(r, None)
    for _Technology, _Generation_Potential_Twh, _Capacity_Potential_GW in r:
        dp[_Technology] = float(_Generation_Potential_Twh)
windPotential = dp["Onshore wind power"] + dp["Offshore wind power"]
solarPotential = dp["Urban utility-scale PV"] + dp["Rural utility-scale PV"] + dp["Rooftop PV"] + dp["Concentrating solar power"]
print "Wind technical potential: %s (%s:1)" % (windPotential,  round(totalEnergyConsumption/windPotential, 1))
print "Solar technical potential: %s (1:%s)" % (solarPotential,  round(solarPotential/totalEnergyConsumption, 1))

def writeSvg(filename, data):
    # sort data
    data = sorted(data, key=lambda k: -k['value'])

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
    circlesPattern = dwg.pattern(id="circles", patternUnits="userSpaceOnUse", size=(6,6))
    circlesPattern.add(dwg.rect(insert=(0,0), size=(6,6), fill="#FFFFFF"))
    circlesPattern.add(dwg.circle(center=(3,3), r=1, fill="#000000"))
    circlesPattern.add(dwg.circle(center=(0,0), r=1, fill="#000000"))
    circlesPattern.add(dwg.circle(center=(0,6), r=1, fill="#000000"))
    circlesPattern.add(dwg.circle(center=(6,0), r=1, fill="#000000"))
    circlesPattern.add(dwg.circle(center=(6,6), r=1, fill="#000000"))
    dwg.defs.add(circlesPattern)
    # wavesPattern = dwg.pattern(id="waves", patternUnits="userSpaceOnUse", size=(20,20))
    # wavesPattern.add(dwg.rect(insert=(0,0), size=(20,20), fill="#FFFFFF"))
    # wavesPattern.add(dwg.path(d="M0 10 c 2.5 -5 , 7.5 -5 , 10 0 c 2.5 5 , 7.5 5 , 10 0 M -10 10 c 2.5 5 , 7.5 5 , 10 0 M 20 10 c 2.5 -5 , 7.5 -5 , 10 0", stroke_width=1, stroke="#000000", stroke_linecap="square", fill="none"))
    wavesPattern = dwg.pattern(id="waves", patternUnits="userSpaceOnUse", size=(48,32), patternTransform="scale(0.75) rotate(45)")
    wavesPattern.add(dwg.rect(insert=(0,0), size=(48,32), fill="#FFFFFF"))
    wavesPattern.add(dwg.path(d="M27 32c0-3.314 2.686-6 6-6 5.523 0 10-4.477 10-10S38.523 6 33 6c-3.314 0-6-2.686-6-6h2c0 2.21 1.79 4 4 4 6.627 0 12 5.373 12 12s-5.373 12-12 12c-2.21 0-4 1.79-4 4h-2zm-6 0c0-3.314-2.686-6-6-6-5.523 0-10-4.477-10-10S9.477 6 15 6c3.314 0 6-2.686 6-6h-2c0 2.21-1.79 4-4 4C8.373 4 3 9.373 3 16s5.373 12 12 12c2.21 0 4 1.79 4 4h2z", fill="#000000"))
    dwg.defs.add(wavesPattern)

    shapes = dwg.add(dwg.g(id="shapes"))
    radius = WIDTH * 0.5
    area = math.pi * math.pow(radius, 2)
    for i, item in enumerate(data):
        itemArea = area * item["value"]
        itemRadius = math.sqrt(itemArea / math.pi)
        offsetY = radius - itemRadius
        x = WIDTH*0.5
        y = HEIGHT*0.5 - offsetY
        y += i * 10
        shapes.add(dwg.circle(center=(x+PAD, y+PAD), r=itemRadius, fill="url(#%s)" % item["pattern"], stroke="#000000", stroke_width=item["width"]))
    dwg.save()
    print "Saved svg: %s" % filename

actualRenewable = windProduction + solarProduction
potentialRenewable = windPotential + solarPotential
maxValue = max([totalEnergyConsumption, actualRenewable, potentialRenewable])
writeSvg(args.OUTPUT_FILE, [
    {"label": "Total energy consumption", "value": totalEnergyConsumption / maxValue, "width": 3, "pattern": "waves"},
    {"label": "Wind and solar production", "value": actualRenewable / maxValue, "width": 3, "pattern": "circles"},
    {"label": "Wind and solar potential", "value": potentialRenewable / maxValue, "width": 3, "pattern": "honeycomb"}
])
