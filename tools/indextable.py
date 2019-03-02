#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-min', nargs='?', type=int, default=1)
parser.add_argument('max', type=int)
parser.add_argument('linkprefix', nargs='?', default='')
args = parser.parse_args()

print('{| class=indextable')
for i in range(args.min, args.max+1):
	print('| [[/{}{}|{}]]'.format(args.linkprefix, i, i))
	if i != args.max and i % 10 == 0:
		print('|-')
print('|}')
