# -*- coding: utf-8 -*-

import json
import numpy as np
import shapefile # https://github.com/GeospatialPython/pyshp

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

    def filterFeatures(self, key, value):
        self.features = [f for f in self.features if key in f["properties"] and f["properties"][key] == value]
        self.getShapes()
        if not len(self.features):
            print "Warning: no feature with %s=%s found" % (key, value)

    def getBounds(self):
        lngs = []
        lats = []
        for shape in self.shapes:
            for lnglat in shape:
                lngs.append(lnglat[0])
                lats.append(lnglat[1])
        minLng = min(lngs)
        maxLng = max(lngs)
        minLat = min(lats)
        maxLat = max(lats)
        return [minLng, minLat, maxLng, maxLat]

    def getDimensions(self):
        bounds = self.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        return (width, height)

    def getShapes(self):
        shapes = []
        for feature in self.features:
            geo = feature["geometry"]
            geoType = geo["type"]
            coordinates = geo["coordinates"]
            if geoType == "Polygon":
                shapes.append(coordinates[0][:])
            elif geoType == "MultiPolygon":
                for c in coordinates:
                    shapes.append(c[0][:])
        self.shapes = shapes

    def onlyBiggestShape(self):
        shapes = sorted(self.shapes, key=lambda s: -1 * self.polygonArea(s))
        if len(shapes):
            self.shapes = [shapes[0]]
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
        for shape in self.shapes:
            polygon = []
            for lnglat in shape:
                x = 1.0 * (lnglat[0] - bounds[0]) / (bounds[2] - bounds[0]) * targetWidth + offsetX
                y = (1.0 - (lnglat[1] - bounds[1]) / (bounds[3] - bounds[1])) * targetHeight + offsetY
                polygon.append((x, y))
            polygons.append(polygon)
        return polygons
