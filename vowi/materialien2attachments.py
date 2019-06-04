#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
import re

import mwbot

def convert_redirect(r):
	before = r['revisions'][0]['*']
	redir = mwbot.parse_redirect(before)
	if redir and redir[0].startswith('http'):
		text = '{{#exturl:%s}}' % redir[0].strip()
		if redir[1] and redir[1] != r['title'].split('/')[-1].replace('_', ' '):
			text += '\n[[Hat Linkbeschreibung::%s]]' % redir[1]
		mwbot.save(site, r['title'], before, text, 'verwende #exturl Parserfunktion')


def convert_redirects(threads):
	results = list(site.results(generator='querypage', gqppage='BrokenRedirects', gqplimit='max', prop='revisions', rvprop='content'))

	with PoolExecutor(max_workers=threads) as executor:
		for _ in executor.map(convert_redirect, results):
			pass

def convert_file(r):
	text = r['revisions'][0]['*']
	parts = text.split("<!-- Don't edit below this line! -->")
	after = parts[0]
	if len(parts) == 2:
		for line in parts[1].splitlines():
			match = re.match('\[\[([^]]+)\]\]', line)
			if match:
				title = match.group(1).strip().replace('_', ' ')
				if not title.startswith('Kategorie'):
					after += '{{#attach:%s}}\n' % title
	else:
		print('cannot handle', r['title'])

	mwbot.save(site, r['title'], text, after, 'verwende #attach Parserfunktion')

def convert_files(threads):
	results = list(site.results(generator='categorymembers', gcmtitle='Category:Materialien', gcmtype='file', prop='revisions', rvprop='content', gcmlimit='max'))
	with PoolExecutor(max_workers=threads) as executor:
		for _ in executor.map(convert_file, results):
			pass

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	parser.add_argument('--threads', default=1, type=int)
	args = parser.parse_args()
	site = mwbot.getsite('materialien2attachments.py', args)
	convert_redirects(args.threads)
	convert_files(args.threads)
