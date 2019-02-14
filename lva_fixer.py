#!/usr/bin/env python3

import argparse

import mwparserfromhell

import mwapp

def handle_template(tpl):
	if tpl.has('wann'):
		if tpl.get('wann').value.strip() == 'Sommersemester':
			tpl.get('wann').value = 'SS\n'
		elif tpl.get('wann').value.strip() == 'Wintersemester':
			tpl.get('wann').value = 'WS\n'
	if tpl.has('sprache'):
		tpl.get('sprache').value = ','.join(s.title() for s in tpl.get('sprache').value.split(','))
	return 'fixe LVA-Daten (lva_fixer.py)'

def handle_page(page):
	before = page.text()
	code = mwparserfromhell.parse(before)
	templates = code.filter_templates(matches = lambda t: t.name.matches('LVA-Daten'))
	if templates:
		msg = handle_template(templates[0])
		mwapp.save(page, before, str(code), msg)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('page', nargs='?')
	args = parser.parse_args()
	site = mwapp.getsite()
	if args.page:
		handle_page(site.pages[args.page])
	else:
		for page in site.categories['LVAs']:
			if page.namespace in mwapp.UNI_NAMESPACES:
				handle_page(page)
