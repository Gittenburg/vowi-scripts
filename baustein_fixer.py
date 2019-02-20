#!/usr/bin/python3
import argparse

import mwapi
import mwbot
import mwparserfromhell

def handle_page(page):
	orig = page['revisions'][0]['*']
	code = mwparserfromhell.parse(orig)
	for div in code.ifilter_tags(matches=lambda x: x.tag == 'div'):
		code.replace(div, div.contents)
	new = str(code)
	if not code.filter_templates(matches=lambda x: x.name.matches('Baustein footer')):
		new += '\n{{Baustein footer}}'
	if not code.filter_headings():
		new = '====== ' + page['title'].split(':')[1] + ' ======\n' + new
	mwbot.save(site, page['title'], orig, new, 'fixe Textbaustein (bausteien_fixer.py)')

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	mwbot.add_pagesel_args(parser, categorydefault='Textbausteine für Beispiele')
	args = parser.parse_args()
	site = mwbot.getsite()
	
	mwbot.handle_pagesel_args(site, args, (mwapi.NS_TEMPLATE,), handle_page)
