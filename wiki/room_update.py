#!/usr/bin/env python3
import re
import json

import mwbot
from mwbot import set_param_value, set_param_name
from mwparserfromhell.nodes import Template, Text
from mwparserfromhell.wikicode import Wikicode

with open('rooms.json') as f:
	rooms = json.load(f)

def handle_template(tpl, room, namespace=None):
	if not tpl.has('name') or tpl.get('name').value.strip() != room['name']:
		tpl.add('name', room['name'])
	if not tpl.has('tiss_code') or tpl.get('tiss_code').value.strip() != room['tiss_code']:
		tpl.add('tiss_code', room['tiss_code'])
	if not tpl.has('capacity') or tpl.get('capacity').value.strip() != str(room['capacity']):
		tpl.add('capacity', room['capacity'])
	if not tpl.has('address') or tpl.get('address').value.strip() != str(room['addr']):
		tpl.add('address', room['addr'])
	return 'update room data (from TISS)'

def handle_page(page):
	before = page['revisions'][0]['*']
	code = mwbot.parse(before)
	templates = code.filter_templates(matches = lambda t: t.name.matches('Room'))
	rcode = page['title'].split(':')[-1]
	if templates and rcode in rooms:
		msg = handle_template(templates[0], rooms[rcode], page['ns'])
		mwbot.save(site, page['title'], before, str(code), site.msg(msg), strip_consec_nl=True)

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	mwbot.add_pagesel_args(parser, categorydefault='Rooms')
	args = parser.parse_args()
	site = mwbot.getsite('room_update.py', args)
	mwbot.handle_pagesel_args(site, args, (3000,), handle_page)
