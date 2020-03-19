#!/usr/bin/env python3
import urllib.parse
import json
import re
import sys

import requests
import lxml.etree
import lxml.html

if __name__ == '__main__':
	html = ''
	page = 0

	while True:
		print('requesting page {}', page, file=sys.stderr)
		res = requests.post('https://tiss.tuwien.ac.at/events/selectRoom.xhtml', data={
			'dspwid': 4960,
			'javax.faces.partial.ajax': 'true',
			'javax.faces.partial.execute': 'tableForm:roomTbl',
			'javax.faces.partial.render': 'tableForm:roomTbl',
			'javax.faces.source': 'tableForm:roomTbl',
			'tableForm:roomTbl': 'tableForm:roomTbl',
			'tableForm:roomTbl_encodeFeature': 'true',
			'tableForm:roomTbl_first': 30 * page,
			'tableForm:roomTbl_rows': 30,
			'tableForm:roomTbl_pagination': 'true',
			'tableForm:roomTbl_skipChildren': 'true'
		})
		res = lxml.etree.fromstring(res.content).find('.//update').text
		if res:
			html += res
			page += 1
		else:
			break

	data = {}
	blacklist = set()

	suffix = re.compile('- Achtung! Werkraum, kein Hörsaal!| - Achtung! Werkraum, kein Seminarraum!')

	for row in lxml.html.fromstring(html):
		link = row[0].find('a')
		code = re.sub(' +', '', row[-1].text or '')
		if code in data:
			blacklist.add(code)
		room = dict(
			name = suffix.sub('', link.text).replace('Sem.R.', 'Seminarraum').strip(),
			capacity = int(lxml.html.tostring(row[1], method='text', encoding='unicode')),
			tiss_code = urllib.parse.unquote(link.get('href').split('=')[-1]).strip(),
			addr = row[-2].text.strip().rstrip(',')
		)
		if code in blacklist:
			print('##duplicate##', file=sys.stderr)
			if code in data:
				print(json.dumps(data[code]), file=sys.stderr)
				del data[code]
			print(json.dumps(room), file=sys.stderr)
		else:
			data[code] = room
	print(json.dumps(data))
