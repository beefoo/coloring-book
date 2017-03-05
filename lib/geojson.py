# -*- coding: utf-8 -*-

import json
import math
import numpy as np
import shapefile # https://github.com/GeospatialPython/pyshp
import sys

def mercator(radians):
    return math.log(math.tan(radians*0.5 + math.pi*0.25))

class GeoJSONUtil:

    def __init__(self, filename, key=None, value=None):
        geojson = None
        if filename.endswith("json"):
            with open(filename) as f:
                geojson = json.load(f)
        else:
            geojson = self.shapefileToGeojson(filename)
        if geojson:
            self.features = geojson["features"]
            if key is not None and value is not None:
                self.filterFeatures(key, value)
            else:
                self.getShapes()

    # http://stackoverflow.com/questions/2651099/convert-long-lat-to-pixel-x-y-on-a-given-picture
    # http://gis.stackexchange.com/questions/71643/map-projection-lat-lon-to-pixel
    def coordinateToPixel(self, lnglat, w, h, bounds):
        west = math.radians(bounds[0])
        south = math.radians(bounds[1])
        east = math.radians(bounds[2])
        north = math.radians(bounds[3])

        ymin = mercator(south)
        ymax = mercator(north)
        xFactor = 1.0 * w / (east - west)
        yFactor = 1.0 * h / (ymax - ymin)

        x = math.radians(lnglat[0])
        y = mercator(math.radians(lnglat[1]))
        x = (x - west) * xFactor
        y = (ymax - y) * yFactor # y points south
        return (x, y)

    def filterFeatures(self, key, value):
        self.features = [f for f in self.features if key in f["properties"] and f["properties"][key] == value]
        self.getShapes()
        if not len(self.features):
            print "Warning: no feature with %s=%s found" % (key, value)

    def getBounds(self):
        lngs = []
        lats = []
        for featureShapes in self.shapes:
            for featureShape in featureShapes:
                for lnglat in featureShape:
                    lngs.append(lnglat[0])
                    lats.append(lnglat[1])
        minLng = min(lngs)
        maxLng = max(lngs)
        minLat = min(lats)
        maxLat = max(lats)
        return [minLng, minLat, maxLng, maxLat]

    def getDimensions(self):
        bounds = self.getBounds()
        west = math.radians(bounds[0])
        south = math.radians(bounds[1])
        east = math.radians(bounds[2])
        north = math.radians(bounds[3])
        ymin = mercator(south)
        ymax = mercator(north)
        width = (east - west)
        height = (ymax - ymin)
        return (width, height)

    def getProperties(self, key):
        properties = [f["properties"][key] for f in self.features]
        return properties

    def getShapes(self):
        shapes = []
        for feature in self.features:
            geo = feature["geometry"]
            geoType = geo["type"]
            coordinates = geo["coordinates"]
            featureShapes = []
            if geoType == "Polygon":
                for c in coordinates:
                    featureShapes.append(c[:])
            elif geoType == "MultiPolygon":
                for mc in coordinates:
                    for c in mc:
                        featureShapes.append(c[:])
            # sort by size and add
            featureShapes = sorted(featureShapes, key=lambda s: -1 * self.polygonArea(s))
            shapes.append(featureShapes)
        self.shapes = shapes

    def onlyBiggestShape(self):
        shapes = sorted(self.shapes, key=lambda s: -1 * self.polygonArea(s[0]))
        if len(shapes):
            self.shapes = [[shapes[0][0]]]
        else:
            self.shapes = []

    # http://stackoverflow.com/a/30408825
    def polygonArea(self, points):
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

    def rejectFeatures(self, key, value):
        self.features = [f for f in self.features if key not in f["properties"] or f["properties"][key] != value]
        self.getShapes()
        if not len(self.features):
            print "Warning: features reduced to zero"

    def shapefileToGeojson(self, filename):
        # convert shapefile to geojson
        sf = shapefile.Reader(filename)
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

    def toPolygons(self, targetWidth, offsetX=0, offsetY=0):
        polygons = []
        bounds = self.getBounds()
        (w, h) = self.getDimensions()
        targetHeight = 1.0 * targetWidth * (1.0 * h / w)
        for featureShapes in self.shapes:
            featurePolygons = []
            for featureShape in featureShapes:
                featurePolygon = []
                for lnglat in featureShape:
                    (x, y) = self.coordinateToPixel(lnglat, targetWidth, targetHeight, bounds)
                    # x = 1.0 * (lnglat[0] - bounds[0]) / (bounds[2] - bounds[0]) * targetWidth + offsetX
                    # y = (1.0 - (lnglat[1] - bounds[1]) / (bounds[3] - bounds[1])) * targetHeight + offsetY
                    featurePolygon.append((x + offsetX, y + offsetY))
                featurePolygons.append(featurePolygon)
            polygons.append(featurePolygons)
        return polygons
