.. Lines starting with two dots are special commands. But if no command can be found, the line is considered as a comment

=========================================================
Main titles are written using equals signs over and under
=========================================================

Note that there must be as many equals signs as title characters.

Title are underlined with equals signs too
==========================================

Subtitles with dashes
---------------------

You can put text in *italic* or in **bold**, you can "mark" text as code with double backquote ``print()``.

Special characters can be escaped using a backslash, e.g. \\ or \*.

Lists are similar to Markdown, but a little more involved.

Remember to line up list symbols (like - or \*) with the left edge of the previous text block, and remember to use blank lines to separate new lists from parent lists:    

- First item
- Second item

  - Sub item

- Third item

or

* First item
* Second item

  * Sub item

* Third item

Tables are really easy to write:

=========== ========
Country     Capital
=========== ========
France      Paris
Japan       Tokyo
=========== ========

More complex tables can be done easily (merged columns and/or rows) but I suggest you to read the complete doc for this :)

There are multiple ways to make links:

- By adding an underscore after a word : Github_ and by adding the target URL after the text (this way has the advantage to not insert unnecessary URLs inside readable text).
- By typing a full comprehensible URL : https://github.com/ (will be automatically converted to a link)
- By making a more Markdown-like link: `Github <https://github.com/>`_ .

.. _Github: https://github.com/