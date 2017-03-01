# -*- coding: utf-8 -*-

# Description: generates set of images that can be printed as a book
# Example usage:
#   python make_ebook.py -basedir ../../Dropbox/coloring_book/book/

import argparse
import csv
import math
import os
from fpdf import FPDF
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-basedir', dest="BASE_DIR", default="", help="Base directory")
parser.add_argument('-manifests', dest="INPUT_MANIFEST_FILES", default="sequence_default", help="Comma-separated list of manifest file names")
parser.add_argument('-manifestdir', dest="MANIFEST_DIR", default="manifest/", help="Directory of manifest files")
parser.add_argument('-inputdir', dest="INPUT_DIR", default="print/", help="Directory of input files/pages")
parser.add_argument('-outputdir', dest="OUTPUT_DIR", default="compiled/", help="Directory for output files")
parser.add_argument('-width', dest="WIDTH", type=float, default=8.5, help="Width of pdf")
parser.add_argument('-height', dest="HEIGHT", type=float, default=11.0, help="Height of pdf")

# init input
args = parser.parse_args()
BASE_DIR = args.BASE_DIR
MANIFEST_DIR = BASE_DIR + args.MANIFEST_DIR
INPUT_MANIFEST_FILES = [MANIFEST_DIR + f + '.csv' for f in args.INPUT_MANIFEST_FILES.split(",")]
INPUT_DIR = BASE_DIR + args.INPUT_DIR
OUTPUT_DIR = BASE_DIR + args.OUTPUT_DIR

# config page
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT

# ensure output dir exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# read manifest files
manifest_files = []
for mf in INPUT_MANIFEST_FILES:
    with open(mf) as f:
        r = csv.DictReader(f)
        pages = []
        for row in r:
            row["file"] = INPUT_DIR + row["file"]
            pages.append(row)
        # add manifest file
        manifest_files.append({
            "file": mf,
            "name": os.path.basename(mf).split(".")[0],
            "pages": pages
        })

def makePDF(pages, filename):
    pdf = FPDF(orientation="Portrait", unit="in", format=(WIDTH, HEIGHT))
    for page in pages:
        pdf.add_page()
        pdf.image(page["file"], 0, 0, WIDTH, HEIGHT)
    pdf.output(filename, "F")
    print "Made pdf %s" % filename


# read files from directory
for f in manifest_files:

    # ensure directory exists
    directory = OUTPUT_DIR
    if not os.path.exists(directory):
        os.makedirs(directory)

    # add pages to pdf
    pages = f["pages"]
    filename =  directory + "/" + f["name"]
    makePDF(pages, filename + ".pdf")

    # covers
    covers = [pages.pop(0), pages.pop()]
    makePDF(covers, filename + "-covers.pdf")

    # even pages
    evens = [p for i, p in enumerate(pages) if i % 2 <= 0]
    makePDF(evens, filename + "-evens.pdf")

    # odd pages
    odds = [p for i, p in enumerate(pages) if i % 2 > 0]
    makePDF(odds, filename + "-odds.pdf")
