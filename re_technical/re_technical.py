# -*- coding: utf-8 -*-

import argparse
import csv
import math
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=60, help="Padding of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/re_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD

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
    height = WIDTH
    dwg = svgwrite.Drawing(filename, size=(WIDTH+PAD*2, height+PAD*2), profile='full')

    # make patterns
    diagonalPattern = dwg.pattern(id="diagonal", patternUnits="userSpaceOnUse", size=(20,20))
    diagonalPattern.add(dwg.rect(insert=(0,0), size=(20,20), fill="#FFFFFF"))
    diagonalPattern.add(dwg.path(d="M 0,20 l 20,-20 M -5,5 l 10,-10 M 15,25 l 10,-10", stroke_width=1, stroke="#000000"))
    dwg.defs.add(diagonalPattern)
    circlesPattern = dwg.pattern(id="circles", patternUnits="userSpaceOnUse", size=(20,20))
    circlesPattern.add(dwg.rect(insert=(0,0), size=(20,20), fill="#FFFFFF"))
    circlesPattern.add(dwg.circle(center=(10,10), r=5, fill="none", stroke_width=1, stroke="#000000"))
    dwg.defs.add(circlesPattern)
    wavesPattern = dwg.pattern(id="waves", patternUnits="userSpaceOnUse", size=(10,10))
    wavesPattern.add(dwg.rect(insert=(0,0), size=(10,10), fill="#FFFFFF"))
    wavesPattern.add(dwg.path(d="M 0 5 c 1.25 -2.5 , 3.75 -2.5 , 5 0 c 1.25 2.5 , 3.75 2.5 , 5 0 M -5 5 c 1.25 2.5 , 3.75 2.5 , 5 0 M 10 5 c 1.25 -2.5 , 3.75 -2.5 , 5 0", stroke_width=1, stroke="#000000", stroke_linecap="square", fill="none"))
    dwg.defs.add(wavesPattern)

    minRadius = 10
    shapes = dwg.add(dwg.g(id="shapes"))
    radius = WIDTH * 0.5
    area = math.pi * math.pow(radius, 2)
    direction = 1.0
    for i, item in enumerate(data):
        itemArea = area * item["value"]
        itemRadius = max(math.sqrt(itemArea / math.pi), minRadius)
        x = WIDTH*0.5
        y = height*0.5
        # if i > 0:
            # adjust = math.sqrt(math.pow(itemRadius,2)/2)
            # x += (direction * adjust)
            # y += (direction * itemRadius)
            # y += (direction * radius * 0.5)
            # direction *= -1
        shapes.add(dwg.circle(center=(x+PAD, y+PAD), r=itemRadius, fill="url(#%s)" % item["pattern"], stroke="#000000", stroke_width=item["width"]))
    dwg.save()
    print "Saved svg: %s" % filename

maxValue = max([totalEnergyConsumption, windProduction, solarProduction])
writeSvg(args.OUTPUT_FILE % "actual", [
    {"label": "Total energy consumption", "value": totalEnergyConsumption / maxValue, "width": 2, "pattern": "circles"},
    {"label": "Wind energy production", "value": windProduction / maxValue, "width": 2, "pattern": "waves"},
    {"label": "Solar energy production", "value": solarProduction / maxValue, "width": 2, "pattern": "diagonal"}
])

maxValue = max([totalEnergyConsumption, windPotential, solarPotential])
writeSvg(args.OUTPUT_FILE % "potential", [
    {"label": "Total energy consumption", "value": totalEnergyConsumption / maxValue, "width": 2, "pattern": "circles"},
    {"label": "Wind energy technical potential", "value": windPotential / maxValue, "width": 2, "pattern": "waves"},
    {"label": "Solar energy technical potential", "value": solarPotential / maxValue, "width": 2, "pattern": "diagonal"}
])
