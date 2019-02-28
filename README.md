# VoWi

GitHub repository for [VoWi](https://vowi.fsinf.at/) bots, extensions and userscripts.

## Bots

Are written in Python 3 and require [requests](http://docs.python-requests.org/) and [mwparserfromhell](https://github.com/earwig/mwparserfromhell).

* `report.py` -- a script to report on incorrect template usage at `VoWi:Report`
* `lva_fixer.py` -- a script to fix LVA-Daten templates
* `beispiel_fixer.py` -- a script to fix Beispiel templates
* `baustein_fixer.py` -- a script to fix templates in `Kategorie:Textbausteine für Beispiele`
* `mat_mover.py` -- a script to move LVAs with their resources
* `subpage_mover.py` -- a script to move subpages
* `old_mat_counter.py` -- a script to count the number of outdated resources so they can be excluded in the statistics on the main page
* `indextable.py` -- a script to generate index tables

Helper modules:
* `mwapi.py` -- a lightweight MediaWiki API wrapper
* `mwbot.py` -- a bot helper module


Create `<bot>.ini`:

```
[root]
api=https://vowi.fsinf.at/api.php
username=Username
password=Password
```

Scripts can then be run as follows:

	$ ACCT=<bot>.ini ./<script>.py

## Userscripts

Are written in JavaScript and require a userscript manager. [Violentmonkey](https://violentmonkey.github.io/) is recommended.

* `vowi2tiss-search.user.js` -- a userscript to add TISS search links to VoWi LVA pages (does not work with Greasemonkey)
