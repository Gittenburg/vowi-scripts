#!/usr/bin/env python3

import argparse

import mwparserfromhell

import mwapi
import mwbot
from mwbot import set_param_value, set_param_name
import vowi

def handle_template(tpl, namespace=None):
	if tpl.has('wann'):
		if tpl.get('wann').value.strip() in ('Sommersemester', 'ss'):
			set_param_value(tpl, 'wann', 'SS')
		elif tpl.get('wann').value.strip() in ('Wintersemester', 'ws'):
			set_param_value(tpl, 'wann', 'WS')
		elif tpl.get('wann').value.strip() in ('Winter- und Sommersemester', 'Sommer- und Wintersemester'):
			set_param_value(tpl, 'wann', 'beide')
	if tpl.has('sprache'):
		# titleize
		tpl.get('sprache').value = ';'.join(s.title() for s in tpl.get('sprache').value.split(';'))
	if tpl.has('tiss'):
		if tpl.get('tiss').value.strip() == '1234567890':
			tpl.remove('tiss')
	if tpl.has('institut'):
		if not tpl.has('abteilung') and not '[' in tpl.get('institut').value:
			set_param_name(tpl, 'institut', 'abteilung')
	if tpl.has('abteilung'):
		set_param_value(tpl, 'abteilung', ';'.join([s.split('#')[0] for s in str(tpl.get('abteilung').value).replace('_', ' ').split(';')]))

	if tpl.has('zuordnungen'):
		rels = tpl.get('zuordnungen').value.filter_templates()
		for rel in rels:
			if not rel.has('2') and rel.has('wahl'):
				rel.remove('wahl')
		rels.sort(key=lambda x: x.get('1'))
		tpl.get('zuordnungen').value = '\n' + '\n'.join([' '*4 + str(r) for r in rels]) + '\n'

	return 'fixe LVA-Daten (lva_fixer.py)'

def handle_page(title):
	page = next(site.query('pages', prop='revisions', titles=title, rvprop='content'))

	before = page['revisions'][0]['*']
	code = mwparserfromhell.parse(before)
	templates = code.filter_templates(matches = lambda t: t.name.matches('LVA-Daten'))
	if templates:
		msg = handle_template(templates[0], page['ns'])
		mwbot.save(site, title, before, str(code), msg)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('page', nargs='?')
	parser.add_argument('-c', dest='category', default='LVAs')
	args = parser.parse_args()
	site = mwbot.getsite()
	namespaces = site.get('query', meta='siteinfo', siprop='namespaces')['query']['namespaces']
	if args.page:
		handle_page(args.page)
	else:
		for page in site.query('categorymembers', list='categorymembers', cmtitle='Category:'+args.category, cmnamespace=mwapi.join(vowi.UNI_NAMESPACES)):
			print(page['title'])
			handle_page(page['title'])
