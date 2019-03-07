# VoWi

GitHub repository for [VoWi](https://vowi.fsinf.at/) bots, extensions and userscripts.

## Bots

The `mwbot` module provides a lightweight MediaWiki API wrapper.

`general/` contains scripts useful for any MediaWiki installation:

* `rollback.py` -- undo changes by a user with a specific edit summary (useful to undo batch edits of bots)
* `subpage_mover.py` -- move subpages, checking for collisions beforehand and without being limited to [$wgMaximumMovedPages](https://www.mediawiki.org/wiki/Manual:$wgMaximumMovedPages)

`vowi/` contains VoWi-specific scripts:

* `mat_mover.py` -- move LVAs with their [resources](https://fs.fsinf.at/wiki/Resources)
* `bsp_mover.py` -- move Beispiele to a new semester
* `lva_fixer.py` -- a script to fix LVA-Daten templates
* `bsp_fixer.py` -- a script to fix Beispiel templates
* `baustein_fixer.py` -- a script to fix templates in `Kategorie:Textbausteine für Beispiele`
* `gen_bsptable.py` -- a script to generate beispiel tables
* `report.py` -- report on incorrect template usage at `VoWi:Report`
* `old_mat_counter.py` -- a script to count the number of outdated resources so they can be excluded in the statistics on the main page

### Installation

Install [Python 3](https://www.python.org/) and the [requests](http://docs.python-requests.org/) and [mwparserfromhell](https://github.com/earwig/mwparserfromhell) packages:

    $ pip3 install requests mwparserfromhell

Install the `mwbot` package:

    $ pip3 install -e ./mwbot

Create an `.ini` file with the following:

```
[root]
api=https://vowi.fsinf.at/api.php
username=Your Username
password=Your Password
```

Scripts can then be run as follows:

	$ ACCT=your.ini ./script.py

## Userscripts

Are written in JavaScript and require a userscript manager. [Violentmonkey](https://violentmonkey.github.io/) is recommended.

* `vowi2tiss-search.user.js` -- a userscript to add TISS search links to VoWi LVA pages (does not work with Greasemonkey)
