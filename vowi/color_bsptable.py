#!/usr/bin/env python3
import logging
import sys

import mwparserfromhell

import mwbot

def handle(site, page):
	result = site.complete(titles=page, generator='links', redirects=True, prop='revisions', rvprop='content', gpllimit='max')

	classes_per_title = {}

	for bsp in result['pages'].values():
		classes = []
		if not 'missing' in bsp:
			bspcode = mwparserfromhell.parse(bsp['revisions'][0]['*'], skip_style_tags=True)
			if bspcode.filter_templates(matches=lambda t: t.name.matches('ungelöst')):
				continue

			templates = bspcode.filter_templates(matches=lambda t: t.name.matches('Beispiel'))
			if len(templates):
				tpl = templates[0]

				if tpl.has('teils') and tpl.get('teils').value.strip() != '':
					classes.append('beispiel-teils')

				status = tpl.get('status').value.strip().lower() if tpl.has('status') else None

				if status in ('datei', 'extern'):
					classes.append('beispiel-{}'.format(status))
				elif tpl.has('1') and tpl.get('1').value.strip() != '':
					classes.append('beispiel-wikicode')
		if classes:
			classes_per_title[bsp['title']] = classes
			if 'redirects' in result:
				for r in result['redirects']:
					if r['to'] == bsp['title']:
						classes_per_title[r['from']] = classes
						if not bsp['title'].startswith(page):
							classes_per_title[r['from']].append('beispiel-redirect')

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

	mwbot.save(site, page, idxpage['revisions'][0]['*'], str(code), site.msg('update'))

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	parser.add_argument('page', nargs='?')
	args = parser.parse_args()

	site = mwbot.getsite('color_bsptable.py', args)
	try:
		if args.page:
			handle(site, args.page)
		else:
			for title in site.get('askargs', conditions='Category:Beispielindexe|Ist veraltet::0', parameters='limit=9999')['query']['results']:
				print(title)
				handle(site, title)
	except KeyboardInterrupt as e:
		sys.exit()
