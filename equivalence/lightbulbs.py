# -*- coding: utf-8 -*-

import svgwrite

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 2.82 x 10-2 metric tons CO2 / bulb replaced
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#incanbulb
LIGHTBULB_REDUCTIONS = 0.0282

# 40 lightbulbs per U.S. household
# https://www.energystar.gov/ia/partners/manuf_res/CFL_PRG_FINAL.pdf
LIGHTBULBS_PER_HOUSEHOLD = 40

# Households replacing incandescent bulbs with LED bulbs necessary to take one car off the road for a year
households = int(round(VEHICLE_EMISSIONS / (LIGHTBULB_REDUCTIONS * LIGHTBULBS_PER_HOUSEHOLD)))
print "%s households necessary." % households

# (Should be 4)
