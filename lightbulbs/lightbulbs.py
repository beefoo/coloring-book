# -*- coding: utf-8 -*-

import svgwrite

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
