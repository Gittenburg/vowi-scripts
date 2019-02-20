import configparser
import os
import sys
import os.path
import difflib

import mwparserfromhell

import mwapi

def add_pagesel_args(parser, categorydefault=None):
	parser.add_argument('page', nargs='?')
	parser.add_argument('-c', dest='category', default=categorydefault)

def handle_pagesel_args(site, args, namespaces, callback):
	if args.page:
		callback(next(site.query('pages', prop='revisions', titles=args.page, rvprop='content')))
	else:
		for page in site.query('pages', generator='categorymembers', gcmtitle='Category:'+args.category,
				gcmnamespace=mwapi.join(namespaces), prop='revisions', rvprop='content', gcmlimit='max'):
			callback(page)

def getsite():
	if 'ACCT' not in os.environ:
		sys.exit('ACCT environment variable not set')
	config = configparser.ConfigParser()
	config.read(os.environ['ACCT'])
	site = mwapi.Site(config['root']['api'])
	site.login(config['root']['username'], config['root']['password'])
	return site

def ensure_enabled(site, scriptname=None):
	if scriptname is not None:
		tree = mwparserfromhell.parse(site.pages['user:'+site.username].text())
		for row in tree.filter_tags(matches=lambda t: t.tag.matches('tr')):
			if row.contents.nodes[0].contents.matches(scriptname):
				if row.contents.nodes[1].contents.matches('ENABLED'):
					break
		else:
			sys.exit('script not ENABLED on user page')

def diff(before, after):
	print('\n'.join(difflib.unified_diff(before.splitlines(), str(after).splitlines())))

def edit(site, title, text, summary):
	site.post('edit', title=title, text=text, summary=summary, token=site.token(), bot=1, **{'assert': 'bot'})

def save(site, title, before, after, msg, ask=True):
	if str(before) == str(after):
		return False
	print('title:', title)
	if type(msg) == list:
		msg = ', '.join(msg)
	print('msg: {}'.format(msg))
	diff(before, after)
	if not ask or 'NOASK' in os.environ or input() == '':
		edit(site, title, str(after), msg)


def set_param_value(tpl, name, value):
	oldval = tpl.get(name).value
	tpl.get(name).value = ' '*(oldval.startswith(' ') and not value.startswith(' ')) + value + '\n'*(not value.endswith('\n'))

def set_param_name(tpl, name, newname):
	tpl.get(name).name = str(tpl.get(name).name).replace(name, newname)

def santitle(a):
	a = str(a).replace('_', ' ').strip()
	return a[0].lower() + a[1:]
