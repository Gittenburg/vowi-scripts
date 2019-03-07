#!/usr/bin/env python3
import mwbot
import mwparserfromhell
import vowi

if __name__ == '__main__':
	parser = mwbot.get_argparser()
	parser.add_argument('page')
	args = parser.parse_args()

	site = mwbot.getsite('bsp_convert_legacy.py', args)

	index = next(site.results(titles=args.page, prop='revisions', rvprop='content'))
	code = mwparserfromhell.parse(index['revisions'][0]['*'])
	moves = []

	for iw in code.ifilter_wikilinks():
		if not str(iw.title).startswith('/') and '/Übungen' in str(iw.title):
			moves.append((str(iw.title), '/'.join(index['title'].split('/')[:2]) + '/Beispiel ' + str(iw.text)))

	mwbot.moves(site, moves, 'verschiebe zu semester {}'.format(index['title'].split('/')[1].split()[1]))
