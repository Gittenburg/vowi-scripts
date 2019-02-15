#!/usr/bin/env python3

import argparse

import mwparserfromhell

import mwapp
from mwapp import setparam

def handle_template(tpl, namespace=None):
	if tpl.has('wann'):
		if tpl.get('wann').value.strip() in ('Sommersemester', 'ss'):
			setparam(tpl, 'wann', 'SS')
		elif tpl.get('wann').value.strip() in ('Wintersemester', 'ws'):
			setparam(tpl, 'wann', 'WS')
		elif tpl.get('wann').value.strip() in ('Winter- und Sommersemester', 'Sommer- und Wintersemester'):
			setparam(tpl, 'wann', 'beide')
	if tpl.has('sprache'):
		# titleize
		tpl.get('sprache').value = ';'.join(s.title() for s in tpl.get('sprache').value.split(';'))
	if tpl.has('tiss'):
		if tpl.get('tiss').value.strip() == '1234567890':
			tpl.remove('tiss')
	if namespace == mwapp.NS_TU_WIEN:
		pass

	return 'fixe LVA-Daten (lva_fixer.py)'

def handle_page(page):
	before = page.text()
	code = mwparserfromhell.parse(before)
	templates = code.filter_templates(matches = lambda t: t.name.matches('LVA-Daten'))
	if templates:
		msg = handle_template(templates[0], page.namespace)
		mwapp.save(page, before, str(code), msg)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('page', nargs='?')
	args = parser.parse_args()
	site = mwapp.getsite()
	namespaces = site.namespaces
	if args.page:
		handle_page(site.pages[args.page])
	else:
		for page in site.categories['LVAs']:
			if mwapp.is_uni_ns(page.namespace):
				handle_page(page)
