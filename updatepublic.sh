#!/bin/sh
rm -Rf kanjivg.xml.gz data
./mergexml.py
outFile="kanjivg-`date +\"%Y%m%d\"`.tar.gz"
tar cvzf $outFile data
gzip $outFile
scp $outFile.gz gnurou@gnurou.org:/srv/http/kanjivg/upload/Main/
scp Main.StrokeCountMismatch Main.MissingKanji gnurou@gnurou.org:/srv/http/kanjivg/wiki.d
#ssh gnurou@gnurou.org "cd /srv/http/kanjivg ; rm -Rf currentdata ; tar xfz /home/gnurou/currentdata.tar.gz ; rm /home/gnurou/currentdata.tar.gz ; cd upload/Main ; ln -sf $outFile.gz kanjivg-latest.xml.gz"

