# MissingFunctions

[This extension](https://github.com/Gittenburg/vowi/tree/master/MissingFunctions) should work for MediaWiki 1.31.1 and higher and only provides two [parser functions](https://www.mediawiki.org/wiki/Manual:Parser_functions):

* `{{#maptemplate:text|template|insep|outsep}}`<br>
  Splits the provided text on *insep*, wrapping each part in the given *template*, optionally followed by an *outsep*.
  For example: `{{#maptemplate:one;two;three|foo|;|,}}` &rarr; `{{foo|one}},{{foo|two}},{{foo|three}}`.
  *insep* and *outsep* understand `\n` as a newline and support &lt;nowiki> tags, which are necessary for leading or trailing whitespace (for example `, <nowiki/>`).
* `{{#frametitle:level}}`<br>
  This functions allows templates to access their own page title (level 0) or the title of a parent page (level > 0). *level* can be omitted, in which case it defaults to 0. To better illustrate how it works, imagine the following page structure:<br>
  Page A: `{{B}}`, Template:B: `{{C}}`, Template:C `{{#frametitle:level}}`
  * level 0 (or no level) would always return "Template:C"
  * level 1 would return "Template:B" on page A and Template:B
  * level 2 would return "A" on page A

## Why missing?

`#maptemplate` is necessary if you don't want to require your contributors to wrap every value in a template themselves and are not using [Extension:Page Forms](https://www.mediawiki.org/wiki/Extension:Page_Forms), which [provides a similar function](https://www.mediawiki.org/wiki/Extension:Page_Forms/Page_Forms_and_templates#arraymaptemplate), this function is inspired by. Semantic MediaWiki's `#set` function [also provides a template parameter](https://www.semantic-mediawiki.org/wiki/Help:Setting_values/Working_with_the_template_parameter), which can act as a maptemplate but however inevitably sets an SMW property for every value, which can be undesirable. While the [#explode parser function](https://www.mediawiki.org/wiki/Extension:StringFunctions##explode:) can be used to approximate the functionality for a limited number of values, it also limits the string length to `$wgPFStringLenghtLimit` and does not support extension tags.

The MediaWiki [page name magic words](https://www.mediawiki.org/wiki/Help:Magic_words#Page_names) only work on the title of the topmost page, which is why `#frametitle` is necessary, if you want templates to access their own title, while embedded. For example, you can have multiple templates include their title as a heading without the titles and headings being able to get out of sync. The functionality of `#frametitle` does not appear to be provided by any other extension.
