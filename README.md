# Fix UTF-8 encoding of EPUB files

This script edits ill-formatted EPUB files to ensure that they specifies the UTF-8 encoding.

EPUB files that don't specify this are interpreted as Windows-1252 characters by default on many platforms and the resulting ebook has a lot of unwanted characters. This [this link](https://string-functions.com/encodingtable.aspx?encoding=65001&decoding=1252) for more details on the encoding errors.
