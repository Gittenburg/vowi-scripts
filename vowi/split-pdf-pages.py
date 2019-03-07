#!/usr/bin/env python3
# Modified from https://stackoverflow.com/a/15741856/1301753

import argparse
import copy
import sys
import math

import PyPDF2

def split_pages(src, dst):
	reader = PyPDF2.PdfFileReader(open(src, 'r+b'))
	output = PyPDF2.PdfFileWriter()

	for i in range(reader.getNumPages()):
	    p = reader.getPage(i)
	    q = copy.copy(p)
	    q.mediaBox = copy.copy(p.mediaBox)

	    x1, x2 = p.mediaBox.lowerLeft
	    x3, x4 = p.mediaBox.upperRight

	    x1, x2 = math.floor(x1), math.floor(x2)
	    x3, x4 = math.floor(x3), math.floor(x4)
	    x5, x6 = math.floor(x3/2), math.floor(x4/2)

	    if x3 > x4:
	        # horizontal
	        q.mediaBox.upperRight = (x5, x4)
	        q.mediaBox.lowerLeft = (x1, x2)

	        p.mediaBox.upperRight = (x3, x4)
	        p.mediaBox.lowerLeft = (x5, x2)
	    else:
	        # vertical
	        q.mediaBox.upperRight = (x3, x4)
	        q.mediaBox.lowerLeft = (x1, x6)

	        p.mediaBox.upperRight = (x3, x6)
	        p.mediaBox.lowerLeft = (x1, x2)

	    output.addPage(p)
	    output.addPage(q)

	with open(dst, 'w+b') as f:
		output.write(f)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input')
	parser.add_argument('output', nargs='?')
	args = parser.parse_args()
	if args.output is None:
		args.output = args.input.replace('.pdf', '.cropped.pdf')
	split_pages(args.input, args.output)
