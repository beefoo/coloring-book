# -*- coding: utf-8 -*-

import argparse
import inspect
import json
import math
import os
import shapefile # https://github.com/GeospatialPython/pyshp
import svgwrite
from svgwrite import inch, px
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.mathutils as mu

# input
parser = argparse.ArgumentParser()
# input source: http://nsidc.org/data/docs/noaa/g02135_seaice_index/
parser.add_argument('-input', dest="INPUT_FILE", default="data/extent_N_{month}_polygon_v2/extent_N_{month}_polygon_v2", help="Path to input shapefiles")
parser.add_argument('-before', dest="MONTH_BEFORE", default="199609", help="Month before loss")
parser.add_argument('-after', dest="MONTH_AFTER", default="201609", help="Months after loss")
parser.add_argument('-width', dest="WIDTH", type=int, default=800, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-simplify', dest="SIMPLIFY", type=int, default=100, help="Points to simplify to")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/extent_N_polygon_v2.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD

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

def lnglatToPx(lnglat, bounds, width, height, pad=0):
    x = 1.0 * (lnglat[0] - bounds[0]) / (bounds[2] - bounds[0]) * width
    y = (1.0 - 1.0 * (lnglat[1] - bounds[1]) / (bounds[3] - bounds[1])) * height
    # return (int(round(x)), int(round(y)))
    x += pad
    y += pad
    return (x, y)

def featuresToSvg(features, svgfile):
    if not len(features):
        return False

    # get bounds
    bounds = boundaries(features)

    # aspect ratio: w / h
    aspect_ratio = 1.0 * abs(bounds[2]-bounds[0]) / abs(bounds[3]-bounds[1])
    height = WIDTH / aspect_ratio

    # Init svg
    dwg = svgwrite.Drawing(svgfile, size=((WIDTH+PAD*2)*px, (height+PAD*2)*px), profile='full')
    center = (0.5*(WIDTH+PAD*2), 0.5*(height+PAD*2))

    # Add features to svg
    for i, feature in enumerate(features):
        featureId = feature["id"]
        points = []
        for lnglat in feature["coordinates"]:
            point = lnglatToPx(lnglat, bounds, WIDTH, height, PAD)
            points.append(point)
        points = mu.smoothPoints(points, feature["smoothResolution"], feature["smoothSigma"])
        # simplify points
        if "simplifyTo" in feature:
            points = mu.simplify(points, feature["simplifyTo"] + 1)
            removeLast = points.pop()
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
                dwgGroup.add(dwg.circle(center=point, r=3))
            dwgTextGroup = dwg.add(dwg.g(id=featureId+"_labels"))
            if "label" in feature:
                for j, point in enumerate(points):
                    rad = mu.radiansBetweenPoints(center, point)
                    # round to nearest X degrees
                    rad = mu.roundToNearestDegree(rad, 45)
                    tp = mu.translatePoint(point, rad, feature["textTranslate"])
                    dwgTextGroup.add(dwg.text(str(j+1), insert=tp, text_anchor="middle", alignment_baseline="middle", font_size=feature["fontSize"]))
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
sfname = args.INPUT_FILE.replace("{month}", args.MONTH_AFTER)
geojson = shapeToGeojson(sfname)
# reduce the set to just the largest polygon
polygon = largestPolygon(geojson)
features.append({
    "id": "month" + args.MONTH_AFTER,
    "type": "Polygon",
    "coordinates": polygon,
    "smoothResolution": 3,
    "smoothSigma": 1.8
})

# convert shapefile to geojson
sfname = args.INPUT_FILE.replace("{month}", args.MONTH_BEFORE)
geojson = shapeToGeojson(sfname)
# reduce the set to just the largest polygon
polygon = largestPolygon(geojson)
features.append({
    "id": "month" + args.MONTH_BEFORE,
    "type": "MultiPoint",
    "coordinates": polygon,
    "smoothResolution": 1.8,
    "smoothSigma": 2,
    "simplifyTo": args.SIMPLIFY,
    "label": "number",
    "textTranslate": 15,
    "fontSize": 12
})

featuresToSvg(features, args.OUTPUT_FILE)
