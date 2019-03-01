#!/usr/bin/env python3
import argparse

import mwbot

parser = argparse.ArgumentParser()
parser.add_argument('user')
parser.add_argument('comment')
args = parser.parse_args()

site = mwbot.getsite()

pageids = []

for uc in site.query('usercontribs', list='usercontribs', ucuser=args.user, uclimit='max'):
	if uc['comment'] == args.comment:
		if uc['pageid'] not in pageids:
			pageids.append(uc['pageid'])
			revisions = next(site.query('pages', prop='revisions', titles=uc['title'], rvlimit=10, rvprop='content|user|ids|comment'))['revisions']
			if revisions[0]['user'] != args.user:
				print('{}: latest edit not by user'.format(uc['revid']))
			else:
				lastother = None
				steps = 0
				for rev in revisions:
					if rev['user'] != args.user or rev['comment'] != args.comment:
						lastother = rev
						break
					steps += 1
				mwbot.save(site, uc['title'], revisions[0]['*'], lastother['*'], 'Revert last {} edits by [[User:{}]] (rollback.py)'.format(steps, args.user))
