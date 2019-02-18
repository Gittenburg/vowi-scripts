import configparser
import os
import sys
import os.path
import difflib

import mwparserfromhell

import mw

NS_TU_WIEN = 3000
NS_UNI_WIEN = 3002
NS_MU_WIEN = 3004
NS_SONSTIGE = 3006

UNI_NAMESPACES = (
	NS_TU_WIEN,
	NS_UNI_WIEN,
	NS_MU_WIEN,
	NS_SONSTIGE
)

def getsite():
	if 'ACCT' not in os.environ:
		sys.exit('ACCT environment variable not set')
	config = configparser.ConfigParser()
	config.read(os.environ['ACCT'])
	site = mw.Site(config['root']['api'])
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

def save(site, title, before, after, msg):
	if str(before) == str(after):
		return False
	if type(msg) == list:
		msg = ', '.join(msg)
	print('msg: {}'.format(msg))
	diff(before, after)
	if 'NOASK' in os.environ or input() == '':
		site.post('edit', title=title, text=str(after), summary=msg, token=site.token(), **{'assert': 'bot'})


def set_param_value(tpl, name, value):
	oldval = tpl.get(name).value
	tpl.get(name).value = ' '*(oldval.startswith(' ') and not value.startswith(' ')) + value + '\n'*(not value.endswith('\n'))

def set_param_name(tpl, name, newname):
	tpl.get(name).name = str(tpl.get(name).name).replace(name, newname)

def santitle(a):
	a = str(a).replace('_', ' ').strip()
	return a[0].lower() + a[1:]
