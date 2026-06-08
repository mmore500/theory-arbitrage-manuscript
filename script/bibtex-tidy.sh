#!/bin/bash

set -e -o pipefail # exit with error if any of this fails

script_dir="$(dirname "$(readlink -f "$0")")"

cd "${script_dir}"
cd ..

cp bibl.bib /tmp/bibl.bib
bibtex-tidy --omit=abstract,keywords --curly --numeric --space=2 --align=0 --sort=key --duplicates=key,doi --merge=combine --strip-enclosing-braces --no-escape --sort-fields=title,shorttitle,author,year,month,day,journal,booktitle,location,on,publisher,address,series,volume,number,pages,doi,isbn,issn,url,urldate,copyright,category,note,metadata --trailing-commas --remove-empty-fields - < bibl.bib > /tmp/bibl-tidy.bib
mv /tmp/bibl-tidy.bib bibl.bib
