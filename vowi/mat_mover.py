#!/usr/bin/env python3
import argparse
import sys
import re

import mwbot

"""
Not using move subpages functionality because it does
not check if the destination exists beforehand.
"""

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	parser.add_argument('src')
	parser.add_argument('dest')
	parser.add_argument('reason', nargs='?', default='LVA-Umbenennung')
	args = parser.parse_args()

	site = mwbot.getsite('mat_mover.py', args)
	site.require_rights('edit', 'move', 'movefile', 'markbotedits')

	srcpage = next(site.results(prop='info', titles=args.src))
	if 'missing' in srcpage:
		sys.exit("fatal: src doesn't exist")

	moves = {srcpage['pageid']: args.dest} #dict from_id -> to_title

	for subpage in site.results(list='prefixsearch', pssearch=args.src + '/', pslimit='max'):
		name = subpage['title'][len(args.src)+1:]
		moves[subpage['pageid']] = args.dest + '/' + name
		print('subpage', name)

	datei_prefix = 'Datei:'+args.src.replace(':','-') + ' - '

	ziel_dateien = []
	for datei in site.results(list='backlinks', bltitle=args.src, blnamespace=mwbot.NS_FILE):
		name = datei['title'][len(datei_prefix):]
		dest = 'Datei:'+args.dest.replace(':','-') + ' - ' + name
		ziel_dateien.append(str(datei['pageid']))
		if datei['title'] != dest and datei['title'].startswith(datei_prefix):
			moves[datei['pageid']] = dest
			print('file   ', name)

	for page in site.results(prop='redirects', titles=mwbot.join(moves.values())):
		if not 'missing' in page: # page exists
			if 'redirects' in page:
				for r in page['redirects']:
					if r['pageid'] in moves and moves[r['pageid']] == r['title']:
						break
				else:
					del moves[r['pageid']]
					continue
			sys.exit('aborting: destination "{}" already exists'.format(dest))

	if input(('no collisions found, are you sure you want to move src to dest?\n'
			  'src:  {}\n'
			  'dest: {}\n').format(args.src, args.dest)) != '':
		sys.exit()

	for src, dest in moves.items():
		print(src, dest)
		site.post('move', fromid=src, to=dest, reason=site.msg(args.reason), movetalk=1, movesubpages=0, token=site.token())

	# update backlinks (the way Materialien work)
	if ziel_dateien:
		for datei in site.results(prop='revisions', pageids='|'.join(ziel_dateien), rvprop='content'):
			orig = datei['revisions'][0]['*']
			code = mwbot.parse(orig)
			for link in code.ifilter_wikilinks():
				link_target = mwbot.santitle(link.title)
				san_dest = mwbot.santitle(args.src)
				link_target, isspecial = re.subn('[sS]pe[cz]ial: *([mM]aterialien|[rR]esources)/', '', link_target)

				if mwbot.santitle(link_target) == san_dest:
					link.title = 'Spezial:Materialien/'*isspecial + args.dest
			site.post('edit', pageid=datei['pageid'], text=str(code), summary=site.msg('update LVA backlink'), token=site.token(), bot=1)
