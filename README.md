# VoWi

GitHub repository for [VoWi](https://vowi.fsinf.at/) bots and extensions.

* `mwapi.py` -- a lightweight MediaWiki API wrapper
* `mwbot.py` -- a bot helper module
* `lva_fixer.py` -- a script to fix LVA-Daten templates
* `mat_mover.py` -- a script to move LVAs with their resources

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
