#!/bin/sh
d=`date +%Y%m%d`
outFileOne="kanjivg-$d.xml.gz"
outFileAll="kanjivg-$d-all.zip"
zip -r $outFileAll kanji
python createsinglerelease.py
gzip -c kanjivg.xml >$outFileOne
scp $outFileOne $outFileAll gnurou@gnurou.org:/srv/http/kanjivg/upload/Main/
ssh gnurou@gnurou.org "ln -sf $outFileOne /srv/http/kanjivg/upload/Main/kanjivg-latest.xml.gz"
