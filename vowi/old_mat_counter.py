#!/usr/bin/env python3
import argparse

import mwapi
import mwbot
import vowi

def count_old_resources():
	old_lvas = []

	for title in site.get('askargs', conditions='Category:LVAs|Ist veraltet::1', parameters='limit=9999')['query']['results']:
		old_lvas.append(title)
		old_resources = 0

	for page in site.results(generator='categorymembers', gcmtitle='Category:Materialien',
			gcmnamespace=mwapi.NS_FILE, gcmlimit='max', prop='links', pllimit='max'):
		
		if 'links' in page:
			for link in page['links']:
				if link['title'] not in old_lvas:
					break
			else:
				old_resources += 1
		else:
			print('no links:', page['title'])

	for page in site.results(list='categorymembers', cmtitle='Category:Materialien',
			cmnamespace=mwapi.join(vowi.UNI_NAMESPACES), cmlimit='max'):
		if page['title'].split('/')[0] in old_lvas:
			old_resources += 1
	return old_resources

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--dry', action='store_true')
	args = parser.parse_args()

	site = mwbot.getsite()

	count = count_old_resources()
	print(count)
	if not args.dry:
		mwbot.edit(site, 'VoWi:Anzahl veralteter Materialien', '{}<noinclude>__NOINDEX__ (generiert von old_mat_counter.py)</noinclude>'.format(count), 'update')