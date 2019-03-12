#!/usr/bin/env python3
import argparse

import mwbot
import vowi

def count_excluded_resources():
	current_lvas = []

	for title in site.get('askargs', conditions='Category:LVAs|Ist veraltet::0', parameters='limit=9999')['query']['results']:
		current_lvas.append(title)

	duplicates = []
	excluded = 0

	for page in site.results(generator='allpages', gapnamespace=mwbot.NS_FILE,
			gaplimit='max', prop='links|duplicatefiles', pllimit='max', dflimit='max'):

		if page['title'] in duplicates:
			excluded += 1
		elif 'links' in page:
			for link in page['links']:
				if link['title'] in current_lvas:
					if 'duplicatefiles' in page:
						for dup in page['duplicatefiles']:
							duplicates.append('Datei:'+dup['name'].replace('_', ' '))
					break
				else:
					excluded += 1

	for ns in vowi.UNI_NAMESPACES:
		for p in site.results(list='allpages', apfilterredir='nonredirects', apnamespace=ns, aplimit='max'):
			if '/' in p['title']:
				if not p['title'].split('/', 1)[0] in current_lvas:
					excluded += 1

	return excluded

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	args = parser.parse_args()

	site = mwbot.getsite('excluded_mat_counter.py', args)

	count = count_excluded_resources()
	print(count)
	mwbot.save(site, 'Vorlage:!materialien anzahl/exkludiert', None, count, site.msg('update'))
