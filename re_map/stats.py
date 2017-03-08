# -*- coding: utf-8 -*-

# Table 1.1.A. Net Generation from Renewable Sources: Total (All Sectors), 2006-December 2016
# https://www.eia.gov/electricity/monthly/epm_table_grapher.cfm?t=epmt_1_01_a

# Wind/solar potential / U.S. / 2012 / Terawatt Hours:
# http://www.nrel.gov/gis/re_potential.html

# 2016 / Estimated Total Solar Generation / Thousand Megawatt-hours
SOLAR_PRODUCTION = 56221 / 1000.0

# 2016 / Wind / Thousand Megawatt-hours
WIND_PRODUCTION = 226485 / 1000.0

# 2012 / Solar potential / Terawatt-hours
SOLAR_POTENTIAL = 2200 + 280600 + 800 + 16100

# 2012 / Wind potential / Terawatt-hours
WIND_POTENTIAL = 32700 + 17000

print "Utilizing %s%% of solar technical potential in 2016." % round(SOLAR_PRODUCTION / SOLAR_POTENTIAL * 100, 2)
print "Utilizing %s%% of wind technical potential in 2016." % round(WIND_PRODUCTION / WIND_POTENTIAL * 100, 2)
