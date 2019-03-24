#!/usr/bin/python3
import argparse

import mwapi
import mwbot

def handle_page(page):
	orig = page['revisions'][0]['*']
	code = mwbot.parse(orig)
	for div in code.ifilter_tags(matches=lambda x: x.tag == 'div'):
		code.replace(div, div.contents)
	new = str(code).strip()
	if not code.filter_templates(matches=lambda x: x.name.matches('Baustein footer')):
		new += '\n{{Baustein footer}}'
	if not code.filter_headings():
		new = '====== ' + page['title'].split(':')[1] + ' ======\n' + new
	mwbot.save(site, page['title'], orig, new, 'fixe Textbaustein (bausteien_fixer.py)')
	if mwbot.santitle(page['title'].split(':')[1]) not in templates:
		undocumented_templates.append(page['title'].split(':')[1])


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	overview = 'Hilfe:Vorlagen für Beispiele'
	mwbot.add_pagesel_args(parser, categorydefault='Textbausteine für Beispiele')
	args = parser.parse_args()
	site = mwbot.getsite()

	page = next(site.query('pages', prop='revisions', titles=overview, rvprop='content'))
	orig = page['revisions'][0]['*']
	code = mwbot.parse(orig)
	templates = [mwbot.santitle(t.name) for t in code.ifilter_templates()]
	undocumented_templates = []

	mwbot.handle_pagesel_args(site, args, (mwapi.NS_TEMPLATE,), handle_page)
	undocumented_templates.sort()
	new = orig
	for t in undocumented_templates:
		new += '\n{{%s}}' % t
	mwbot.save(site, overview, orig, new, '+nichteingeordnete Vorlagen (baustein_fixer.py)')
