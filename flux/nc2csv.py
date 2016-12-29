# -*- coding: utf-8 -*-

import csv
import math
from netCDF4 import Dataset
import sys

# source: ftp://aftp.cmdl.noaa.gov/products/carbontracker/co2/fluxes/monthly/
# info: https://www.esrl.noaa.gov/gmd/ccgg/carbontracker/fluxmaps.php?type=us
# version: CT2015 1x1 3-hourly fluxes as of 2016-02-20 06:38:03 UTC
# averaging_period: 2001-2014 mean
# conversions: http://cdiac.ornl.gov/pns/convert.html

INPUT_FILE = 'data/CT2015.flux1x1.longterm.nc'
OUTPUT_FILE = 'data/CT2015_flux1x1_longterm.csv'

def ncdump(nc_fid, verb=True):
    def print_ncattr(key):
        try:
            print "\t\ttype:", repr(nc_fid.variables[key].dtype)
            for ncattr in nc_fid.variables[key].ncattrs():
                print '\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr))
        except KeyError:
            print "\t\tWARNING: %s does not contain variable attributes" % key
    # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        print "NetCDF Global Attributes:"
        for nc_attr in nc_attrs:
            print '\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        print "NetCDF dimension information:"
        for dim in nc_dims:
            print "\tName:", dim
            print "\t\tsize:", len(nc_fid.dimensions[dim])
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        print "NetCDF variable information:"
        for var in nc_vars:
            if var not in nc_dims:
                print '\tName:', var
                print "\t\tdimensions:", nc_fid.variables[var].dimensions
                print "\t\tsize:", nc_fid.variables[var].size
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars

ds = Dataset(INPUT_FILE, 'r')
# print ds
# nc_attrs, nc_dims, nc_vars = ncdump(ds)

# Extract data from NetCDF file
lats = ds.variables['lat'][:]
lons = ds.variables['lon'][:]
fffs = ds.variables['fossil_flux_imp'][:][0]

# Source: http://www.pmel.noaa.gov/maillists/tmap/ferret_users/fu_2004/msg00023.html
def latLonArea(lat1, lon1, lat2, lon2):
    R = 6371 # radius of Earth in km
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    A = math.pow(R, 2) * abs(math.sin(lat1)-math.sin(lat2)) * abs(lon1-lon2)
    return A

rows = []
for y, lat in enumerate(lats):
    for x, lon in enumerate(lons):
        # print "%s, %s, %s" % (lat, lon, fffs[y][x])
        # CO2 exchange in mols per square meter per second
        mol_m_2_s_1 = fffs[y][x]
        # seconds to years
        mol_m_2_y_1 = mol_m_2_s_1 * 3600 * 24 * 365.25
        # mols to grams
        g_m_2_y_1 = mol_m_2_y_1 * 44.009
        # CO2 exchange in grams per square kilometer per year
        g_km_2_y_1 = g_m_2_y_1 * 1000000
        # # area of lat/lon in km^2
        # lat_lon_km2 = latLonArea(math.floor(lat), math.floor(lon), math.ceil(lat), math.ceil(lon))
        # # square kilometer to 1x1-degree
        # g_degree_2_y_1 = g_km_2_y_1 * lat_lon_km2
        # # grams to tons
        # ton_km_2_y_1 = g_km_2_y_1 / 1000000
        # # CO2 exchange in metric tons per 1x1-degree per year
        # ton_degree_2_y_1 = g_degree_2_y_1 / 1000000
        rows.append([lat, lon, g_km_2_y_1])

print "Printing %s rows to file" % len(rows)

header = ["lat", "lon", "ff_flux"]

with open(OUTPUT_FILE, 'wb') as f:
    cw = csv.writer(f, delimiter=',')
    cw.writerow(header)
    for row in rows:
        cw.writerow(row)

print "Wrote %s rows to file %s" % (len(rows), OUTPUT_FILE)
