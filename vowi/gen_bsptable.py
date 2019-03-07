#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-min', nargs='?', type=int, default=1)
parser.add_argument('max', type=int)
parser.add_argument('linkprefix', nargs='?', default='Beispiel ')
args = parser.parse_args()

print('{| class=beispiel-table')
for i in range(args.min, args.max+1):
	print('||[[/{}{}|{}]]'.format(args.linkprefix, i, i))
	if i != args.max and i % 10 == 0:
		print('|-')
	if i != args.max and i % 100 == 0:
		print('|}')
		print('{| class=beispiel-table')
print('|}')
