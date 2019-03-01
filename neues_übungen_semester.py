#!/usr/bin/env python3
import argparse
import datetime
import re
import sys

import mwbot
import mwapi

def handle(site, page, dry):
	src_page = next(site.query('pages', prop='info|revisions|templates', titles=page, rvprop='content'))
	assert 'Vorlage:Beispielindex' in [t['title'] for t in src_page['templates']]

	today = datetime.datetime.today()
	month = today.month
	semester = ('WS' if month == 1 or month > 9 else 'SS') + str(today.year)[2:]

	def new_title(old_title):
		return str(page[:-4]) + semester + str(old_title[len(page):])

	print('new title:', new_title(page))

	pageids = []   # using ids instead of titles because the request URL is limited
	redirects = {} # {title: target}

	for subpage in site.query('allpages', list='allpages', apprefix=page.split(':', 2)[1]+'/Beispiel ', apnamespace=src_page['ns'], aplimit='max'):
		pageids.append(subpage['pageid'])
		redirects[new_title(subpage['title'])] = subpage['title']

	for redir in site.query('redirects', pageids=mwapi.join(pageids), redirects=True):
		if redir['to'].startswith(page):
			redir['to'] = new_title(redir['to'])
		assert new_title(redir['from']) in redirects
		redirects[new_title(redir['from'])] = redir['to']

	if not dry:
		try:
			mwbot.edit(site, new_title(page), src_page['revisions'][0]['*'], 'kopiert von [[{}]] (neues_übungen_semester.py)'.format(src_page['title']), createonly=True)
		except mwapi.MWException as e:
			if e.args[0]['code'] != 'articleexists':
				raise e

	for idx, (title, target) in enumerate(sorted(redirects.items()), 1):
		if dry:
			print('from:', title)
			print('to:  ', target)
		else:
			print(title)
			try:
				mwbot.edit(site, title, '#redirect [[{}]]'.format(target), 'erstelle Weiterleitung ({}/{}) (neues_übungen_semester.py)'.format(idx, len(redirects)), createonly=True)
			except mwapi.MWException as e:
				if e.args[0]['code'] != 'articleexists':
					raise e

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('page')
	parser.add_argument('--dry', action='store_true')
	args = parser.parse_args()

	site = mwbot.getsite()
	try:
		handle(site, args.page, args.dry)
	except KeyboardInterrupt as e:
		sys.exit()
