#!/usr/bin/env python3
import re

import mwbot
from mwbot import set_param_value, set_param_name
import vowi

def handle_template(tpl, namespace=None):
	if tpl.has('sprache'):
		if tpl.get('sprache').value.strip().lower() in ('englisch', 'english'):
			set_param_value(tpl, 'sprache', 'en')
		if tpl.get('sprache').value.strip().lower() in ('deutsch', 'german'):
			set_param_value(tpl, 'sprache', 'de')

	if tpl.has('wann'):
		if tpl.get('wann').value.strip() in ('Sommersemester', 'ss'):
			set_param_value(tpl, 'wann', 'SS')
		elif tpl.get('wann').value.strip() in ('Wintersemester', 'ws'):
			set_param_value(tpl, 'wann', 'WS')
		elif tpl.get('wann').value.strip() in ('Winter- und Sommersemester', 'Sommer- und Wintersemester'):
			set_param_value(tpl, 'wann', 'beide')
	if tpl.has('tiss'):
		if tpl.get('tiss').value.strip() == '1234567890':
			tpl.remove('tiss')
	if tpl.has('institut'):
		# [http://www.example.com/institutsowieso Institut Sowieso]
		if not tpl.has('abteilung'):
			if not '[' in tpl.get('institut').value:
				set_param_name(tpl, 'institut', 'abteilung')
			else:
				val = str(tpl.get('institut').value)
				m = re.search('E?0?\d\d\d([-/]\d+)?', val)
				if m:
					match = m.group().replace('-', '/')
					if match in abteilungen:
						tpl.get('institut').value = abteilungen[match].split(':')[1]
						tpl.get('institut').name = 'abteilung'
	if tpl.has('abteilung'):
		set_param_value(tpl, 'abteilung', ';'.join([s.split('#')[0] for s in str(tpl.get('abteilung').value).replace('_', ' ').split(';')]))

	if tpl.has('zuordnungen'):
		rels = tpl.get('zuordnungen').value.filter_templates()
		for rel in rels:
			if rel.has('2'):
				rel.get('2').value = str(rel.get('2').value).replace('–', '-')
			elif rel.has('wahl'):
				rel.remove('wahl')
		rels.sort(key=lambda x: x.get('1'))
		tpl.get('zuordnungen').value = '\n' + '\n'.join([' '*4 + str(r) for r in rels]) + '\n'

	return 'fixe LVA-Daten'

def handle_page(page):
	before = page['revisions'][0]['*']
	code = mwbot.parse(before)
	templates = code.filter_templates(matches = lambda t: t.name.matches('LVA-Daten'))
	if templates:
		msg = handle_template(templates[0], page['ns'])
		mwbot.save(site, page['title'], before, str(code), site.msg(msg))

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	mwbot.add_pagesel_args(parser, categorydefault='LVAs')
	args = parser.parse_args()
	site = mwbot.getsite('lva_fixer.py', args)

	abteilungen = {} # id to title
	for title, abt in site.get('askargs', conditions='Kategorie:Abteilungen', printouts='Hat ID|Hatte ID', parameters='limit=999')['query']['results'].items():
		if abt['printouts']['Hat ID']:
			abteilungen[abt['printouts']['Hat ID'][0]] = title
		if abt['printouts']['Hatte ID']:
			abteilungen[abt['printouts']['Hatte ID'][0]] = title

	mwbot.handle_pagesel_args(site, args, vowi.UNI_NAMESPACES, handle_page)
