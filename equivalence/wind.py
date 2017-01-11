# -*- coding: utf-8 -*-

import svgwrite

# 4.73 metric tons CO2E /vehicle/year
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#vehicles
VEHICLE_EMISSIONS = 4.73

# 3,960 metric tons CO2 / wind turbine installed
# https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references#turbine
WIND_TURBINE_REDUCTIONS = 3960

# Vehicles offset per year per garbage truck of waste recycled instead of landfilled
vehicles = int(round(WIND_TURBINE_REDUCTIONS / VEHICLE_EMISSIONS))
print "%s vehicles offset." % vehicles

# (Should be 837)
