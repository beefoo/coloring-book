# -*- coding: utf-8 -*-

import argparse
import inspect
import json
import math
import os
import shapefile # https://github.com/GeospatialPython/pyshp
import svgwrite
import sys

# add parent directory to sys path to import relative modules
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import lib.mathutils as mu
import lib.svgutils as svgu

# input
parser = argparse.ArgumentParser()
# input source: http://nsidc.org/data/docs/noaa/g02135_seaice_index/
parser.add_argument('-input', dest="INPUT_FILE", default="data/extent_N_{month}_polygon_v2/extent_N_{month}_polygon_v2", help="Path to input shapefiles")
parser.add_argument('-before', dest="MONTH_BEFORE", default="199609", help="Month before loss")
parser.add_argument('-after', dest="MONTH_AFTER", default="201609", help="Months after loss")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of output file")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11, help="Height of output file")
parser.add_argument('-pad', dest="PAD", type=float, default=0.5, help="Padding of output file")
parser.add_argument('-simplify', dest="SIMPLIFY", type=int, default=100, help="Points to simplify to")
parser.add_argument('-output', dest="OUTPUT_FILE", default="data/extent_N_polygon_v2.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
DPI = 72
PAD = args.PAD * DPI
WIDTH = args.WIDTH * DPI - PAD * 2
HEIGHT = args.HEIGHT * DPI - PAD * 2

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

def distanceBetweenCoordinates(c1, c2):
    (lon1, lat1) = c1
    (lon2, lat2) = c2
    R = 6371 # km
    dLat = math.radians(lat2-lat1)
    dLon = math.radians(lon2-lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = math.sin(dLat*0.5) * math.sin(dLat*0.5) + math.sin(dLon*0.5) * math.sin(dLon*0.5) * math.cos(lat1) * math.cos(lat2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

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

def lnglatToPx(lnglat, bounds, width, height, offset=(0,0)):
    x = 1.0 * (lnglat[0] - bounds[0]) / (bounds[2] - bounds[0]) * width
    y = (1.0 - 1.0 * (lnglat[1] - bounds[1]) / (bounds[3] - bounds[1])) * height
    # return (int(round(x)), int(round(y)))
    x += offset[0]
    y += offset[1]
    return (x, y)

def featuresToSvg(features, svgfile):
    if not len(features):
        return False

    # get bounds
    bounds = boundaries(features)

    # aspect ratio: w / h
    aspect_ratio = 1.0 * abs(bounds[2]-bounds[0]) / abs(bounds[3]-bounds[1])
    width = WIDTH
    height = width / aspect_ratio
    offsetX = 0
    offsetY = 0
    if height > HEIGHT:
        scale = HEIGHT / height
        width *= scale
        height = HEIGHT
        offsetX = (WIDTH - width) * 0.5
    else:
        offsetY = (HEIGHT - height) * 0.5

    # Init svg
    dwg = svgwrite.Drawing(svgfile, size=(WIDTH+PAD*2, HEIGHT+PAD*2), profile='full')
    dwgLabels = dwg.add(dwg.g(id="labels"))
    center = (0.5*(WIDTH+PAD*2), 0.5*(height+PAD*2))

    # diagonal pattern
    diagonalSize = 18
    diagonalW = 1
    diagonalPattern = dwg.pattern(id="diagonal", patternUnits="userSpaceOnUse", size=(diagonalSize,diagonalSize))
    commands = [
        "M0,%s" % diagonalSize,
        "l%s,-%s" % (diagonalSize, diagonalSize),
        "M-%s,%s" % (diagonalSize*0.25, diagonalSize*0.25),
        "l%s,-%s" % (diagonalSize*0.5, diagonalSize*0.5),
        "M%s,%s" % (diagonalSize-diagonalSize*0.25, diagonalSize+diagonalSize*0.25),
        "l%s,-%s" % (diagonalSize*0.5, diagonalSize*0.5)
    ]
    diagonalPattern.add(dwg.rect(size=(diagonalSize,diagonalSize), fill="#ffffff"))
    diagonalPattern.add(dwg.path(d=commands, stroke_width=diagonalW, stroke="#000000"))
    dwg.defs.add(diagonalPattern)

    # Add features to svg
    for i, feature in enumerate(features):
        featureId = feature["id"]
        # add label
        ab = "after-edge"
        tOffset = -10
        if feature["labelLine"][-1][1] > feature["labelLine"][0][1]:
            ab = "before-edge"
            tOffset *= -1
        tp = feature["labelLine"][-1]
        tp = (tp[0], tp[1]+tOffset)
        dwgLabels.add(dwg.text(feature["label"], insert=tp, text_anchor="middle", alignment_baseline=ab, font_size=12))
        labelLine = dwg.line(start=feature["labelLine"][0], end=feature["labelLine"][-1], stroke="#000000", stroke_width=feature["strokeWidth"])
        if "dashArray" in feature:
            labelLine.dasharray(feature["dashArray"])
        dwg.add(labelLine)
        # get points from lat lon
        points = []
        for lnglat in feature["coordinates"]:
            point = lnglatToPx(lnglat, bounds, width, height, (offsetX+PAD, offsetY+PAD))
            points.append(point)
        points = mu.smoothPoints(points, feature["smoothResolution"], feature["smoothSigma"])
        # simplify points
        if "simplifyTo" in feature:
            points = mu.simplify(points, feature["simplifyTo"] + 1)
            removeLast = points.pop()
        fill = "#FFFFFF"
        if "fill" in feature:
            fill = feature["fill"]
        # add closure for polygons
        points.append((points[0][0], points[0][1]))
        path = svgu.pointsToCurve(points)
        featureLine = dwg.path(id=featureId, d=path, stroke="#000000", stroke_width=feature["strokeWidth"], fill=fill)
        if "dashArray" in feature:
            featureLine.dasharray(feature["dashArray"])
        dwg.add(featureLine)
        # get distance of feature
        # if "distanceLabel" in feature:
        #     lngs = [lnglat[0] for lnglat in feature["coordinates"]]
        #     lats = [lnglat[1] for lnglat in feature["coordinates"]]
        #     meanLng = mu.mean(lngs)
        #     meanLat = mu.mean(lats)
        #     left = [ll for ll in feature["coordinates"] if ll[0] <= meanLng]
        #     right = [ll for ll in feature["coordinates"] if ll[0] > meanLng]
        #     left = sorted(left, key=lambda ll: abs(ll[1]-meanLat))
        #     right = sorted(right, key=lambda ll: abs(ll[1]-meanLat))
        #     c1 = left[0]
        #     c2 = (right[0][0], c1[1])
        #     km = distanceBetweenCoordinates(c1, c2)
        #     print "Total kilometers: %s" % "{:,}".format(km)
        #     p1 = lnglatToPx(c1, bounds, width, height, (offsetX+PAD, offsetY+PAD))
        #     p2 = lnglatToPx(c2, bounds, width, height, (offsetX+PAD, offsetY+PAD))
        #     dwg.add(dwg.line(start=p1, end=p2, stroke="#000000", stroke_width=1))
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
labelX = 0.2 * WIDTH + PAD
labelY = 0.1 * HEIGHT + PAD
features.append({
    "id": "month" + args.MONTH_BEFORE,
    "type": "Polygon",
    "coordinates": polygon,
    "smoothResolution": 3,
    "smoothSigma": 1.8,
    "strokeWidth": 1,
    "dashArray": [3,1],
    "fill": "url(#diagonal)",
    "label": "September 1996",
    "labelLine": [(labelX, PAD + HEIGHT * 0.5), (labelX, labelY)]
})

# convert shapefile to geojson
sfname = args.INPUT_FILE.replace("{month}", args.MONTH_AFTER)
geojson = shapeToGeojson(sfname)
# reduce the set to just the largest polygon
polygon = largestPolygon(geojson)
labelX = 0.65 * WIDTH + PAD
labelY = 0.8 * HEIGHT + PAD
features.append({
    "id": "month" + args.MONTH_AFTER,
    "type": "Polygon",
    "coordinates": polygon,
    "smoothResolution": 3,
    "smoothSigma": 1.8,
    "strokeWidth": 2,
    "label": "September 2016",
    "labelLine": [(labelX, PAD + HEIGHT * 0.5), (labelX, labelY)],
    "distanceLabel": 0.5
})

featuresToSvg(features, args.OUTPUT_FILE)
