#!/usr/bin/python3
import re

import mwbot
from mwparserfromhell.nodes import Template, Text
from mwparserfromhell.wikicode import Wikicode
import vowi

def handle(site, index):
	src_ns = next(site.results(prop='info', titles=index))['ns']

	for page in site.results(generator='allpages', gapprefix=index.split(':')[1] + '/Beispiel ', gaplimit='max', prop='revisions', rvprop='content', gapnamespace=src_ns):
		orig = page['revisions'][0]['*']
		if mwbot.is_redirect(orig):
			continue

		code = mwbot.parse(orig)
		templates = code.filter_templates(matches=lambda x: x.name.matches('Beispiel') or x.name.matches('Bsp'))
		if len(templates) > 0:
			template = templates[0]
		else:
			template = Template(Wikicode([Text('Beispiel')]))
			code.insert(0, template)
			code.insert(1, '\n')

		# legacy format handling
		template.name = 'Beispiel'
		if template.has('status'):
			if str(template.get('status').value).strip() not in ('extern', 'Datei'):
				print('unknown status: {}'.format(k))

		if template.has('gekommen'):
			template.get('gekommen').value = str(template.get('gekommen').value).replace('/', ';')

		if template.has('1'):
			if str(template.get('1').value).strip() == 'teils':
				template.add('teils', '')
				template.remove('1')
			elif str(template.get('1').value).strip() == 'falsch':
				template.add('falsch', '')
				template.remove('1')

		if not template.has('1'):
			angabe_div = code.filter_tags(matches=lambda x: x.tag.matches('blockquote') or len([x for x in x.attributes if '{{Angabe}}' in x or '#EFEFEF' in x]))
			if angabe_div:
				template.add('1', '\n'+str(angabe_div[0].contents).strip()+'\n', showkey=True)
				code.remove(angabe_div[0])
			else:
				angabe_sec = code.get_sections(matches='Angabe|Aufgabe')
				if angabe_sec:
					code.remove(angabe_sec[0].nodes[0])
					template.add('1', '\n'+str(angabe_sec[0]).strip()+'\n', showkey=True)
					code.replace(angabe_sec[0], '\n')

		mwbot.save(site, page['title'], orig, str(code), 'beispiel_fixer.py', strip_consec_nl=True)

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	parser.add_argument('index')
	args = parser.parse_args()

	site = mwbot.getsite('bsp_fixer.py', args)
	handle(site, args.index)
