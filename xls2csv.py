# -*- coding: utf-8 -*-

# Usage:
#   python xls2csv.py -in data/input.xlsx -out output/
#   python xls2csv.py -in data/input.xlsx -out output/ -sheet "Sheet 1"

import argparse
import csv
import os
import sys
import xlrd

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="path/to/file.xlsx", help="Path to input excel file")
parser.add_argument('-sheet', dest="SHEET", default="", help="Sheet name; leave blank to export all")
parser.add_argument('-out', dest="OUTPUT_DIR", default="path/to/csv/dir/", help="Path to output directory")

# init input
args = parser.parse_args()

def excelToCSV(infile, outdir, sheet=""):
    workbook = xlrd.open_workbook(infile)
    worksheets = []

    # ensure output dir exists
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # only get one sheet
    if len(sheet):
        worksheet = workbook.sheet_by_name(sheet)
        worksheets.append({
            'name': sheet,
            'data': worksheet
        })

    # get all sheets
    else:
        for worksheet_name in workbook.sheet_names():
            worksheet = workbook.sheet_by_name(worksheet_name)
            worksheets.append({
                'name': worksheet_name,
                'data': worksheet
            })

    # output sheets as csv
    for ws in worksheets:
        filename = outdir + ws['name'] + '.csv'
        with open(filename, 'wb') as f:
            wr = csv.writer(f)
            for rownum in xrange(ws['data'].nrows):
                wr.writerow([unicode(entry).encode("utf-8") for entry in ws['data'].row_values(rownum)])

excelToCSV(args.INPUT_FILE, args.OUTPUT_DIR, args.SHEET)
