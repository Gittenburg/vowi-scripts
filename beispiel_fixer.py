#!/usr/bin/python3
import argparse
import re

import mwapi
import mwbot
import mwparserfromhell
from mwparserfromhell.nodes import Template, Text
from mwparserfromhell.wikicode import Wikicode
import vowi

def handle_index(site, index):
	src_ns = next(site.query('pages', prop='info', titles=index))['ns']

	for page in site.query('pages', generator='allpages', gapprefix=index.split(':')[1] + '/Beispiel ', gaplimit='max', prop='revisions', rvprop='content', gapnamespace=src_ns):
		orig = page['revisions'][0]['*']
		if mwbot.is_redirect(orig):
			continue

		code = mwparserfromhell.parse(orig)
		templates = code.filter_templates(matches=lambda x: x.name.matches('Beispiel') or x.name.matches('Bsp'))
		if len(templates) > 0:
			template = templates[0]
		else:
			template = Template(Wikicode([Text('Beispiel')]))
			code.insert(0, template)

		# legacy format handling
		template.name = 'Beispiel'
		if template.has('status'):
			fields = template.get('status').value.split(';')
			if len(fields) == 1:
				k = fields[0]
				v = ''
			else:
				k, v = fields
			if k.strip() in ('teils', 'falsch'):
				template.add(k.strip(), v.strip())
				template.remove('status')
			else:
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
				angabe_sec = code.get_sections(matches='Angabe')
				if angabe_sec:
					code.remove(angabe_sec[0].nodes[0])
					template.add('1', '\n'+str(angabe_sec[0]).strip()+'\n', showkey=True)
					code.replace(angabe_sec[0], '\n')

		hilfreiches = code.get_sections(matches='Hilfreiches', include_headings=False)
		if hilfreiches:
			for bstn in hilfreiches[0].filter_templates():
				bstn.name = re.sub('^([Vv]orlage|[Tt]emplate):', '', str(bstn.name))
				if not bstn.name.startswith('Baustein'):
					bstn.name = 'Baustein:' + str(bstn.name)

		mwbot.save(site, page['title'], orig, str(code), 'beispiel_fixer.py', strip_consec_nl=True)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('index')
	args = parser.parse_args()

	site = mwbot.getsite()
	handle_index(site, args.index)
