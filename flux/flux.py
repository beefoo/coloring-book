# -*- coding: utf-8 -*-

import argparse
from collections import Counter
import csv
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.vq import kmeans, vq
import svgwrite
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/CT2015_flux1x1_longterm.csv", help="Input data file")
parser.add_argument('-width', dest="WIDTH", type=int, default=600, help="Width of output file")
parser.add_argument('-pad', dest="PAD", type=int, default=40, help="Padding of output file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/flux_%s.svg", help="Path to output svg file")

# init input
args = parser.parse_args()
WIDTH = args.WIDTH
PAD = args.PAD

lats = 180
lons = 360

data = [[0]*lons for l in range(lats)]
vals = []
# read csv
with open(args.INPUT_FILE, 'rb') as f:
    r = csv.reader(f, delimiter=',')
    # skip header
    next(r, None)
    # put data in matrix
    for y in range(lats):
        for x in range(lons):
            lat, lon, value = next(r)
            data[y][x] = {
                "lat": float(lat),
                "lon": float(lon),
                "value": float(value)
            }
            vals.append(float(value))

landValues = [v for v in vals if v >= 0]
maxValue = max(landValues)
print "Max value: %s" % maxValue

def mean(arr):
    size = len(arr)
    if size <= 0:
        return 0
    return sum(arr) / size


meanValue = mean(landValues)
print "Mean value: %s" % meanValue

# get clusters
y = np.array(landValues)
clusters, distortion = kmeans(y, 5)  # five clusters
cluster_indices, dist = vq(y, clusters)
C = Counter(cluster_indices.tolist())

print "Clusters:"
for k,v in C.items():
    print "Cluster: %s, Size: %s" % (clusters[k], v)

# # show histogram
# ys = []
# for y in range(lats):
#     for x in range(lons):
#         v = data[y][x]["value"]
#         if v >= 0:
#             ys.append(v)
# # plt.bar(range(len(ys)), ys, 1/1.5, color="blue")
# plt.hist(ys, bins=1000, normed=True)
# plt.show()
