#!/usr/bin/env python3
import re

import mwbot
from mwbot import set_param_value, set_param_name
import vowi
from mwparserfromhell.nodes import Template, Text
from mwparserfromhell.wikicode import Wikicode

def handle_template(tpl, code, namespace=None):
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

	archived = False
	successor = None
	if tpl.has('veraltet'):
		archived = True
		tpl.remove('veraltet')
	if tpl.has('nachfolger'):
		archived = True
		successor = tpl.get('nachfolger').value.strip()
		tpl.remove('nachfolger')
	for t in code.ifilter_templates(matches = lambda t: t.name.matches('Veraltet')):
		archived = True
		code.remove(t)
	archivedFlag = code.filter_templates(matches = lambda t: t.name.matches('Archiv'))
	if archived and not archivedFlag:
		tpl = Template(Wikicode([Text('Archiv')]))
		if successor:
			tpl.add('nachfolger', successor)
		code.insert(0, tpl)
		code.insert(1, '\n\n')

	if tpl.has('zuordnungen'):
		rels = tpl.get('zuordnungen').value.filter_templates()
		for rel in rels:
			if rel.has('2'):
				rel.get('2').value = str(rel.get('2').value).replace('–', '-')
		rels.sort(key=lambda x: x.get('1'))
		tpl.get('zuordnungen').value = '\n' + '\n'.join([' '*4 + str(r) for r in rels]) + '\n'

	return 'fixe LVA-Daten'

def handle_page(page):
	before = page['revisions'][0]['*']
	code = mwbot.parse(before)
	templates = code.filter_templates(matches = lambda t: t.name.matches('LVA-Daten'))
	if templates:
		msg = handle_template(templates[0], code, page['ns'])
		mwbot.save(site, page['title'], before, str(code), site.msg(msg), strip_consec_nl=True)

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
