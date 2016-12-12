# -*- coding: utf-8 -*-

import argparse
import json
import numpy as np
from polysimplify import VWSimplifier
from scipy.ndimage import gaussian_filter1d
import shapefile # https://github.com/GeospatialPython/pyshp
import svgwrite
from svgwrite import inch, px
import sys

# input
parser = argparse.ArgumentParser()
# input source: http://nsidc.org/data/docs/noaa/g02135_seaice_index/
parser.add_argument('-input', dest="INPUT_FILE", default="data/extent_N_{month}_polygon_v2/extent_N_{month}_polygon_v2", help="Path to input shapefiles")
parser.add_argument('-before', dest="MONTH_BEFORE", default="199609", help="Month before loss")
parser.add_argument('-after', dest="MONTH_AFTER", default="201609", help="Months after loss")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/extent_N_polygon_v2.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH

# get boundaries
def boundaries(features):
    lngs = []
    lats = []
    for feature in features:
        for lnglat in feature["coordinates"]:
            lngs.append(lnglat[0])
            lats.append(lnglat[1])
    minLng = min(lngs)
    maxLng = max(lngs)
    minLat = min(lats)
    maxLat = max(lats)
    return [minLng, minLat, maxLng, maxLat]

def largestPolygon(geojson):
    coordinates = []
    # Add features to svg
    for i, feature in enumerate(geojson["features"]):
        for coord in feature["geometry"]["coordinates"]:
            coordinates.append({
                "coordinates": coord,
                "length": len(coord)
            })
    coordinates = sorted(coordinates, key=lambda c: c["length"])
    return coordinates[-1]["coordinates"]

def lnglatToPx(lnglat, bounds, width, height):
    x = 1.0 * (lnglat[0] - bounds[0]) / (bounds[2] - bounds[0]) * width
    y = (1.0 - 1.0 * (lnglat[1] - bounds[1]) / (bounds[3] - bounds[1])) * height
    # return (int(round(x)), int(round(y)))
    return (x, y)

# for line simplification
def simplify(line, length=100):
    simplifier = VWSimplifier(line)
    simplified = simplifier.from_number(length)
    return simplified.tolist()

def smoothPoints(points, resolution=3, sigma=1.8):
    a = np.array(points)

    x, y = a.T
    t = np.linspace(0, 1, len(x))
    t2 = np.linspace(0, 1, len(y)*resolution)

    x2 = np.interp(t2, t, x)
    y2 = np.interp(t2, t, y)

    x3 = gaussian_filter1d(x2, sigma)
    y3 = gaussian_filter1d(y2, sigma)

    x4 = np.interp(t, t2, x3)
    y4 = np.interp(t, t2, y3)

    return zip(x4, y4)

def featuresToSvg(features, svgfile):
    if not len(features):
        return False

    # get bounds
    bounds = boundaries(features)

    # aspect ratio: w / h
    aspect_ratio = 1.0 * abs(bounds[2]-bounds[0]) / abs(bounds[3]-bounds[1])
    height = WIDTH / aspect_ratio

    # Init svg
    dwg = svgwrite.Drawing(svgfile, size=(WIDTH*px, height*px), profile='full')

    # Add features to svg
    for i, feature in enumerate(features):
        featureId = feature["id"]
        points = []
        for lnglat in feature["coordinates"]:
            point = lnglatToPx(lnglat, bounds, WIDTH, height)
            points.append(point)
        points = smoothPoints(points)
        # simplify points
        if "simplifyTo" in feature:
            points = simplify(points, feature["simplifyTo"])
        # polygons
        if feature["type"] == "Polygon":
            # add closure for polygons
            points.append((points[0][0], points[0][1]))
            featureLine = dwg.polyline(id=featureId, points=points, stroke="#000000", stroke_width=2, fill="#FFFFFF")
            dwg.add(featureLine)
        # multipoints
        elif feature["type"] == "MultiPoint":
            dwgGroup = dwg.add(dwg.g(id=featureId))
            for point in points:
                dwgGroup.add(dwg.circle(center=point, r=2))
    # Save
    dwg.save()
    print "Saved svg: %s" % svgfile

def shapeToGeojson(sfname):
    # convert shapefile to geojson
    sf = shapefile.Reader(sfname)
    fields = sf.fields[1:]
    field_names = [field[0] for field in fields]
    features = []
    for sr in sf.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": atr
        })
    geojson = {"type": "FeatureCollection", "features": features}
    return geojson

features = []

# convert shapefile to geojson
sfname = args.INPUT_FILE.replace("{month}", args.MONTH_BEFORE)
geojson = shapeToGeojson(sfname)
# reduce the set to just the largest polygon
polygon = largestPolygon(geojson)
features.append({
    "id": "month" + args.MONTH_BEFORE,
    "type": "MultiPoint",
    "coordinates": polygon,
    "simplifyTo": 100
})

# convert shapefile to geojson
sfname = args.INPUT_FILE.replace("{month}", args.MONTH_AFTER)
geojson = shapeToGeojson(sfname)
# reduce the set to just the largest polygon
polygon = largestPolygon(geojson)
features.append({
    "id": "month" + args.MONTH_AFTER,
    "type": "Polygon",
    "coordinates": polygon
})

featuresToSvg(features, args.OUTPUT_FILE)
