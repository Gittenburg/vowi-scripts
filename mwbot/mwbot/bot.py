import argparse
import configparser
import difflib
import logging
import os
import os.path
import re
import sys

logging.basicConfig(level=os.environ.get('LOGLEVEL'))

import mwparserfromhell

from . import api

NS_MAIN = 0
NS_USER = 2
NS_PROJECT = 4
NS_FILE = 6
NS_MEDIAWIKI = 8
NS_TEMPLATE = 10
NS_HELP = 12
NS_CATEGORY = 14

_REDIRECT_RE = re.compile('^\s*#(redirect|weiterleitung)\s*:?\s*\[\[([^]|]+)\|?([^]]*)\]\]', re.IGNORECASE)

def parse(text, **kwargs):
	kwargs.setdefault('skip_style_tags', True)
	return mwparserfromhell.parse(text, **kwargs)

def parse_redirect(code):
	match = _REDIRECT_RE.match(code)
	if match:
		return (match.group(2).strip(), match.group(3).strip())
	else:
		return None

def add_pagesel_args(parser, categorydefault=None):
	parser.add_argument('page', nargs='?')
	parser.add_argument('-c', dest='category', default=categorydefault)

def handle_pagesel_args(site, args, namespaces, callback):
	if args.page:
		callback(next(site.results(prop='revisions', titles=args.page, rvprop='content')))
	else:
		for page in site.results(generator='categorymembers', gcmtitle='Category:'+args.category,
				gcmnamespace=api.join(namespaces), prop='revisions', rvprop='content', gcmlimit='max'):
			callback(page)

def get_argparser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--dry',   action='store_const', help='skip all POST requests', dest='postmode', const=api.Mode.DRY)
	parser.add_argument('--noask', action='store_const', help='do POST requests without confirmation', dest='postmode', const=api.Mode.NOASK)
	return parser

def getsite(scriptname, args):
	if 'ACCT' not in os.environ:
		sys.exit('ACCT environment variable not set')
	config = configparser.ConfigParser()
	config.read(os.environ['ACCT'])
	if args.postmode == None:
		args.postmode = api.Mode.ASK
	site = api.Site(config['root']['api'], scriptname, args.postmode)
	site.login(config['root']['username'], config['root']['password'])
	return site

def diff(before, after):
	print('\n'.join(difflib.unified_diff(before.splitlines(), str(after).splitlines())))

def save(site, title, before, after, msg, ask=True, strip_consec_nl=False, **kwargs):
	if before and str(before) == str(after):
		return False
	print('title:', title)
	if type(msg) == list:
		msg = ', '.join(msg)
	print('msg: {}'.format(msg))
	after = after.strip()
	if ask and site.mode != api.Mode.NOASK:
		if before:
			diff(before, after)
		if input() != '':
			return
	if strip_consec_nl:
		after = re.sub('\n{3,}', '\n\n', str(after))
	site.post('edit', title=title, text=str(after), summary=msg, token=site.token(), bot=1, **{'assert': 'bot'}, **kwargs, skipprompt=True)

def moves(site, moves, reason, **kwargs):
	for src, dest in moves:
		print('from: {}\nto:   {}'.format(src, dest))
	if input() == '':
		for idx, (src, dest) in enumerate(moves, 1):
			print('{}/{}'.format(idx, len(moves)))
			try:
				site.post('move', **{'from':src}, to=dest, reason=site.msg(reason), movetalk=1, movesubpages=1, token=site.token(), skipprompt=True)
			except api.MWException as e:
				if e.args[0]['code'] != 'articleexists':
					raise e

def set_param_value(tpl, name, value):
	oldval = tpl.get(name).value
	tpl.get(name).value = ' '*(oldval.startswith(' ') and not value.startswith(' ')) + value + '\n'*(not value.endswith('\n'))

def set_param_name(tpl, name, newname):
	tpl.get(name).name = str(tpl.get(name).name).replace(name, newname)

def santitle(a):
	a = str(a).replace('_', ' ').strip()
	return a[0].lower() + a[1:]

def ensure_enabled(site, scriptname=None):
	if scriptname is not None:
		tree = mwparserfromhell.parse(site.pages['user:'+site.username].text())
		for row in tree.filter_tags(matches=lambda t: t.tag.matches('tr')):
			if row.contents.nodes[0].contents.matches(scriptname):
				if row.contents.nodes[1].contents.matches('ENABLED'):
					break
		else:
			sys.exit('script not ENABLED on user page')
