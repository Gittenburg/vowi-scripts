import configparser
import os
import sys
import os.path
import difflib

import mwclient
import mwparserfromhell

UNI_NAMESPACES = [3000, 3002, 3004, 3006, 3008]

def getsite():
	if 'ACCT' not in os.environ:
		sys.exit('ACCT environment variable not set')
	config = configparser.ConfigParser()
	config.read(os.environ['ACCT'])
	site = mwclient.Site(config['root']['host'], path=config['root']['path'])
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

def save(page, before, after, msg):
	if str(before) == str(after):
		return False
	if type(msg) == list:
		msg = ', '.join(msg)
	print('msg: {}'.format(msg))
	diff(before, after)
	if 'NOASK' in os.environ or input() == '':
		page.save(str(after), msg)
