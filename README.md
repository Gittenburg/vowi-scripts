# VoWi

GitHub repository um an Bots und Extensions zu arbeiten und Aufgaben zu tracken.

## Bots

Werden in Python 3 geschrieben und benötigen folgende packages:

* [requests](http://docs.python-requests.org/)
* [mwparserfromhell](https://github.com/earwig/mwparserfromhell)

Erstelle `<bot>.ini`:

```
[root]
host=vowi.fsinf.at
path=/
username=Username
password=Password
```

Skripte können dann wie folgt ausgeführt werden:

	$ ACCT=<bot>.ini ./<skript>.py
