#!/usr/bin/env python3
import re

import mwbot
from mwbot import set_param_value, set_param_name
from mwparserfromhell.nodes import Template, Text
from mwparserfromhell.wikicode import Wikicode

def handle_template(tpl, code, namespace=None):
	tpl.name = str(tpl.name).replace('RaumCode', 'room')
	if tpl.has('Address'):
		tpl.get('Address').name = 'address'
	if tpl.has('RoomName'):
		tpl.get('RoomName').name = 'name'
	if tpl.has('RoomSize'):
		tpl.get('RoomSize').name = 'capacity'
	if tpl.has('latitude'):
		tpl.get('latitude').name = 'lat'
	if tpl.has('longitude'):
		tpl.get('longitude').name = 'lng'
	if tpl.has('SearchValue'):
		tpl.get('SearchValue').name = 'alt_name'
	return 'convert to [[Template:Room]]'

def handle_page(page):
	before = page['revisions'][0]['*']
	code = mwbot.parse(before)
	templates = code.filter_templates(matches = lambda t: t.name.matches('RaumCode'))
	if templates:
		msg = handle_template(templates[0], code, page['ns'])
		mwbot.save(site, page['title'], before, str(code).replace('[[Kategorie:Raumcode]]', ''), site.msg(msg), strip_consec_nl=True)

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	mwbot.add_pagesel_args(parser, categorydefault='Raumcode')
	args = parser.parse_args()
	site = mwbot.getsite('raum2room.py', args)
	mwbot.handle_pagesel_args(site, args, (3000,), handle_page)
