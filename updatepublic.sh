#!/bin/sh
rm -Rf kanjivg.xml.gz generated
./mergexml.py
outFile="kanjivg-`date +\"%Y%m%d\"`.xml"
mkdir -p currentdata/SVG
./createsvgfiles.py $outFile
tar czf currentdata.tar.gz currentdata
gzip $outFile
scp $outFile.gz gnurou@gnurou.org:/srv/http/kanjivg/upload/Main/
scp currentdata.tar.gz gnurou@gnurou.org:/home/gnurou
scp Main.StrokeCountMismatch Main.MissingKanji gnurou@gnurou.org:/srv/http/kanjivg/wiki.d
ssh gnurou@gnurou.org "cd /srv/http/kanjivg ; rm -Rf currentdata ; tar xfz /home/gnurou/currentdata.tar.gz ; rm /home/gnurou/currentdata.tar.gz ; cd upload/Main ; ln -sf $outFile.gz kanjivg-latest.xml-gz"

