#!/bin/sh
d=`date +%Y%m%d`
outFileOne="kanjivg-$d.xml.gz"
outFileAll="kanjivg-$d-all.zip"
outFileMain="kanjivg-$d-main.zip"
outFileStripped="kanjivg-$d-stripped.zip"
zip -rq $outFileAll kanji/*.svg
zip -rq $outFileMain kanji/?????.svg
/home/ben/projects/kvgpub/cmd/strip/strip
zip -rq $outFileStripped stripped/*.svg
./kvg.py release
gzip -c kanjivg.xml >$outFileOne
release="r$d"
gh release create --generate-notes --prerelease $release $outFileOne $outFileAll $outFileMain $outFileStripped

