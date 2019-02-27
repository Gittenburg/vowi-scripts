#!/usr/bin/python3
import argparse

import mwapi
import mwbot
import mwparserfromhell
from mwparserfromhell.nodes.template import Template
import vowi

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('index')
	args = parser.parse_args()

	site = mwbot.getsite()

	for page in site.query('pages', generator='allpages', gapprefix=args.index + '/Beispiel ', gaplimit='max', prop='revisions', rvprop='content', gapnamespace=vowi.NS_TU_WIEN):
		orig = page['revisions'][0]['*']
		if mwbot.REDIRECT_RE.match(orig):
			continue
		code = mwparserfromhell.parse(orig)
		templates = code.filter_templates(matches= lambda x: x.name.matches('Beispiel') or x.name.matches('Bsp'))
		if len(templates) == 0:
			code.insert(0, '{{Beispiel}}\n')

		template = code.filter_templates(matches= lambda x: x.name.matches('Beispiel') or x.name.matches('Bsp'))[0]
		template.name='Beispiel'
		if template.has('hilfreiches'):
			template.get('hilfreiches').name = 'bausteine'
		if template.has('gekommen'):
			template.get('gekommen').value = str(template.get('gekommen').value).replace('/', ';')
		if template.has('1'):
			if str(template.get('1').value).strip() == 'teils':
				template.add('status', 'teils')
				template.remove('1')
			elif str(template.get('1').value).strip() == 'falsch':
				template.add('status', 'falsch')
				template.remove('1')
		if template.has('teils'):
			template.add('status', 'teils;'+str(template.get('teils').value))
			template.remove('teils')
		if template.has('falsch'):
			template.add('status', 'falsch;'+str(template.get('falsch').value))
			template.remove('falsch')
	
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
				if not template.has('bausteine'):
					template.add('bausteine', '', preserve_spacing=False)
				if not bstn.name.startswith('Baustein'):
					bstn.name = 'Baustein:' + str(bstn.name)
				if not str(bstn) in str(template.get('bausteine').value):
					template.get('bausteine').value.append('\n' + str(bstn))
				code.remove(bstn)
			if str(hilfreiches[0]).strip() == '':
					code.remove(code.get_sections(matches='Hilfreiches')[0])
		if template.has('bausteine') and not template.get('bausteine').value.endswith('\n'):
			template.get('bausteine').value.append('\n')
		mwbot.save(site, page['title'], orig, str(code).replace('}}\n\n\n', '}}\n\n'), 'beispiel_fixer.py')
