#!/usr/bin/env python3
import argparse
import sys
import re

import mwapi
import mwbot
import mwparserfromhell

"""
Not using move subpages functionality because it does not check if the destination exists beforehand.
"""

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('src')
	parser.add_argument('dest')
	parser.add_argument('reason', nargs='?', default='LVA-Umbenennung')
	args = parser.parse_args()

	site = mwbot.getsite()

	rights = site.myrights()
	for r in ('edit', 'move', 'movefile', 'markbotedits'):
		if r not in rights:
			sys.exit('this script requires the {} right'.format(r))

	srcpage = next(site.query('pages', prop='info', titles=args.src))
	if 'missing' in srcpage:
		sys.exit("fatal: src doesn't exist")

	moves = {srcpage['pageid']: args.dest} #dict from_id -> to_title

	for subpage in site.query('prefixsearch', list='prefixsearch', pssearch=args.src + '/', pslimit='max'):
		name = subpage['title'][len(args.src)+1:]
		moves[subpage['pageid']] = args.dest + '/' + name
		print('subpage', name)

	datei_prefix = 'Datei:'+args.src.replace(':','-') + ' - '

	ziel_dateien = []
	for datei in site.query('backlinks', list='backlinks', bltitle=args.src, blnamespace=mwapi.NS_FILE):
		name = datei['title'][len(datei_prefix):]
		dest = 'Datei:'+args.dest.replace(':','-') + ' - ' + name
		ziel_dateien.append(str(datei['pageid']))
		if datei['title'] != dest and datei['title'].startswith(datei_prefix):
			moves[datei['pageid']] = dest

	for page in site.query('pages', prop='redirects', titles='|'.join(moves.values())):
		if not 'missing' in page: # page exists
			if 'redirects' in page:
				for r in page['redirects']:
					if r['pageid'] in moves and moves[r['pageid']] == r['title']:
						break
				else:
					del moves[r['pageid']]
					continue
			sys.exit('aborting: destination "{}" already exists'.format(dest))

	if input('no collisions found, are you sure you want to move src to dest?\nsrc:  {}\ndest: {}\n'.format(args.src, args.dest)) != '':
		sys.exit()

	for src, dest in moves.items():
		print(src, dest)
		site.post('move', fromid=src, to=dest, reason=args.reason + ' (mat_mover.py)', movetalk=1, movesubpages=0, token=site.token())

	# update backlinks (the way Materialien work)
	if ziel_dateien:
		for datei in site.query('pages', prop='revisions', pageids='|'.join(ziel_dateien), rvprop='content'):
			orig = datei['revisions'][0]['*']
			code = mwparserfromhell.parse(orig)
			for link in code.ifilter_wikilinks():
				link_target = mwbot.santitle(link.title)
				san_dest = mwbot.santitle(args.src)
				link_target, isspecial = re.subn('[sS]pe[cz]ial: *([mM]aterialien|[rR]esources)/', '', link_target)

				if mwbot.santitle(link_target) == san_dest:
					link.title = 'Spezial:Materialien/'*isspecial + args.dest
			site.post('edit', pageid=datei['pageid'], text=str(code), summary='update LVA backlink', token=site.token(), bot=1)
