# VoWi

GitHub repository for [VoWi](https://vowi.fsinf.at/) bots, extensions and userscripts.

* `mwapi.py` -- a lightweight MediaWiki API wrapper
* `mwbot.py` -- a bot helper module
* `lva_fixer.py` -- a script to fix LVA-Daten templates
* `baustein_fixer.py` -- a script to fix templates in `Kategorie:Textbausteine für Beispiele`
* `mat_mover.py` -- a script to move LVAs with their resources
* `old_mat_counter.py` -- a script to count the number of outdated resources so they can be excluded in the statistics on the main page
* `vowi2tiss-search.user.js` -- a userscript to add TISS search links to VoWi LVA pages.

## Bots

Are written in Python 3 and require the following packages:

* [requests](http://docs.python-requests.org/)
* [mwparserfromhell](https://github.com/earwig/mwparserfromhell)

Create `<bot>.ini`:

```
[root]
api=https://vowi.fsinf.at/api.php
username=Username
password=Password
```

Scripts can then be run as follows:

	$ ACCT=<bot>.ini ./<skript>.py
