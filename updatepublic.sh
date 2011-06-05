#!/bin/sh
rm -Rf kanjivg kanjivgMismatch
./mergexml.py
outFile="kanjivg-ng-`date +\"%Y%m%d\"`.zip"
zip -r $outFile kanjivg
scp $outFile gnurou@gnurou.org:/srv/http/kanjivg/upload/Main/
#scp Main.StrokeCountMismatch Main.MissingKanji gnurou@gnurou.org:/srv/http/kanjivg/wiki.d
#ssh gnurou@gnurou.org "cd /srv/http/kanjivg ; rm -Rf currentdata ; tar xfz /home/gnurou/currentdata.tar.gz ; rm /home/gnurou/currentdata.tar.gz ; cd upload/Main ; ln -sf $outFile.gz kanjivg-latest.xml.gz"

