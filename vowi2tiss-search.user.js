// ==UserScript==
// @name TISS Search in VoWi
// @namespace https://vowi.fsinf.at/
// @match https://vowi.fsinf.at/wiki/*
// @match https://tiss.tuwien.ac.at/course/courseList.xhtml*
// ==/UserScript==

if (location.host == 'vowi.fsinf.at') {
	if (document.getElementById('lva-daten') != null) {
		var content = document.getElementById('mw-content-text');
		var a = document.createElement('a');
		a.innerHTML = 'TISS Suche';
		content.insertBefore(a, content.firstChild);
		var title = document.getElementById('firstHeading').innerHTML;
		a.href = 'https://tiss.tuwien.ac.at/course/courseList.xhtml?title=' + encodeURIComponent(
			title.substring(title.indexOf(':') + 1, title.indexOf('(') - 4)
		)
	}
} else if (location.host == 'tiss.tuwien.ac.at') {
	var params = new URL(location).searchParams;
	if (params.get('title')) {
		jsf.ajax.addOnEvent(function (data) {
			if (data.status == 'success') {
				document.getElementById('courseList:courseTitle').value = params.get('title')
				document.getElementById('courseList:semFrom').value = '2015W'
				document.getElementById('courseList:cSearchBtn').click()
			}
		})
		document.getElementById('courseList:quickSearchPanel').children[0].lastElementChild.click()
	}
}
