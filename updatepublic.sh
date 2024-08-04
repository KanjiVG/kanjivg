#!/bin/sh
d=`date +%Y%m%d`
outFileOne="kanjivg-$d.xml.gz"
outFileAll="kanjivg-$d-all.zip"
outFileMain="kanjivg-$d-main.zip"
zip -r $outFileAll kanji/*.svg
zip -r $outFileMain kanji/?????.svg
./kvg.py release
gzip -c kanjivg.xml >$outFileOne
