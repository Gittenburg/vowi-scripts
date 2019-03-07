#!/usr/bin/env python3
import datetime

import mwbot

BSP_PREFIX = 'Beispiel '
FORMAT = '{}/Übungen {}/Beispiel {}'

if __name__ == '__main__':
	today = datetime.datetime.today()
	month = today.month
	semester = ('WS' if month == 1 or month > 9 else 'SS') + str(today.year)[2:]

	parser = mwbot.get_argparser()
	parser.add_argument('index')
	parser.add_argument('from', nargs='?', default='-')
	parser.add_argument('to', nargs='?')
	args = parser.parse_args()

	site = mwbot.getsite('bsp_mover.py', args)

	index = next(site.results(titles=args.index))
	index_parts = index['title'].split('/')
	assert index_parts[1].startswith('Übungen ')
	moves = []

	from_ = getattr(args, 'from')
	if '-' in from_:
		min_, max_ = from_.split('-', 2)
		min_ = int(min_) if min_ else 1
		max_ = int(max_) if max_ else None

		for page in site.results(generator='allpages', gapprefix=args.index.split(':')[1] + '/'+BSP_PREFIX, gaplimit='max', prop='revisions', rvprop='content', gapnamespace=index['ns']):
			if page['title'].count('/') != 2:
				continue
			pagename = page['title'].split('/')[2]
			name = pagename[len(BSP_PREFIX):]
			if name.isdigit():
				if min_ and int(name) < min_:
					continue
				elif max_ and int(name) > max_:
					continue
				else:
					if args.to:
						name = int(name) + (int(args.to) - min_)
					moves.append((page['title'], FORMAT.format(index_parts[0], semester, name)))
	else:
		if args.to is None:
			args.to = from_
		moves.append((args.index + '/Beispiel {}'.format(from_), FORMAT.format(index_parts[0], semester, args.to)))
	if moves:
		for src, dest in moves:
			print('from: {}\nto:   {}'.format(src, dest))
		if input() == '':
			for idx, (src, dest) in enumerate(moves, 1):
				print('{}/{}'.format(idx, len(moves)))
				try:
					site.post('move', **{'from':src}, to=dest, reason=site.msg('verschiebe ins aktuelle Semester'), movetalk=1, movesubpages=1, token=site.token(), skipprompt=True)
				except mwbot.MWException as e:
					if e.args[0]['code'] != 'articleexists':
						raise e
