#!/usr/bin/env python3
import argparse
import os.path

import mwbot

parser = mwbot.get_argparser()
parser.add_argument('src')
parser.add_argument('dest')
parser.add_argument('reason')
parser.add_argument('--noredir', action='store_true')
args = parser.parse_args()

site = mwbot.getsite('subpage_mover.py', args)
site.require_rights('move')

src_ns = next(site.results(list='pages', prop='info', titles=args.src))['ns']

if args.dest.startswith('.'):
	destname = os.path.abspath('/' + args.src + '/' + args.dest)[1:]
	print('resolved destination to {}'.format(destname))
else:
	destname = args.dest

# if noredir, fix backlinks

moves = []

srcname = args.src.split(':', 2)[1]

for page in site.results(list='allpages', apprefix=args.src.split(':', 2)[1]+'/', apnamespace=src_ns, aplimit='max'):
	moves.append((page['title'], destname + page['title'].split(':',2)[1][len(srcname):]))

moves.append((args.src, destname))

for idx, (src, dest) in enumerate(reversed(moves), 1):
	print('move {}/{}:'.format(idx, len(moves)))
	print('from:', src)
	print('to:  ', dest)
	dest = next(site.results(list='pages', titles=dest))
	if not 'missing' in dest:
		if input('destination already exists, skip?') == '':
			del moves[-idx]
		else:
			break
else:
	if input('proceed? redirects: {}'.format(not args.noredir)) == '':
		for src, dest in moves:
			print(src, dest)
			site.post('move', **{'from':src},
					to=dest,
					reason=args.reason + ' (subpage_mover.py)',
					movetalk=True,
					movesubpages=False,
					token=site.token(), noredirect=args.noredir)
