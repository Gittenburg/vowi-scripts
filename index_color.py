#!/usr/bin/env python3
import argparse
import logging
import sys

import mwparserfromhell

import mwapi
import mwbot

def handle(site, page):
	result = site.complete(titles=page, generator='links', redirects=True, prop='revisions', rvprop='content', gpllimit='max')

	classes_per_title = {}

	for bsp in result['pages'].values():
		classes = []
		if not 'missing' in bsp:
			bspcode = mwparserfromhell.parse(bsp['revisions'][0]['*'])
			templates = bspcode.filter_templates(matches=lambda t: t.name.matches('Beispiel'))
			if len(templates):
				tpl = templates[0]
				if tpl.has('status'):
					status = tpl.get('status').value.strip().lower()
					if status in ('datei', 'extern'):
						classes.append('beispiel-{}'.format(status))
				else:
					status = None
				if status not in ('datei', 'extern', 'ungelöst') and tpl.has('1') and tpl.get('1').value.strip() != '':
					classes.append('beispiel-wikicode')
				if tpl.has('teils') and tpl.get('teils').value.strip() != '':
					classes.append('beispiel-teils')
		if classes:
			classes_per_title[bsp['title']] = classes
			for r in result['redirects']:
				if r['to'] == bsp['title']:
					classes_per_title[r['from']] = classes
					if not bsp['title'].startswith(page):
						classes_per_title[r['from']].append('beispiel-alt')

	idxpage = next(site.results(prop='revisions', titles=page, rvprop='content'))
	code = mwparserfromhell.parse(idxpage['revisions'][0]['*'])

	for table in code.filter_tags(matches=lambda t: t.tag.matches('table')):
		table.attributes.clear()
		table.attributes.append(' class=beispiel-table')
		for td in table.contents.filter_tags(matches=lambda t: t.tag.matches('td')):
			links = td.contents.filter_wikilinks()
			if len(links) == 1:
				if links[0].title.startswith('/'):
					td.attributes.clear()
					title = page + str(links[0].title)
					if title in classes_per_title:
						td.attributes.append('class="{}"'.format(' '.join(classes_per_title[title])))
				else:
					logging.info('found non-relative link')
			else:
				logging.info('found cell with {} links'.format(len(links)))

	mwbot.save(site, page, idxpage['revisions'][0]['*'], str(code), 'update (beispielindex_color.py)')

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('page')
	args = parser.parse_args()

	site = mwbot.getsite()
	try:
		handle(site, args.page)
	except KeyboardInterrupt as e:
		sys.exit()
