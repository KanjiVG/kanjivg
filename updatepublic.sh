#!/bin/sh
rm -Rf kanjivg.xml.gz generated
./mergexml.py
mkdir -p currentdata/SVG
./createsvgfiles.py
tar czf currentdata.tar.gz currentdata
gzip kanjivg.xml
scp kanjivg.xml.gz gnurou@gnurou.org:/srv/http/kanjivg/upload/Main/kanjivg-latest.xml.gz
scp currentdata.tar.gz gnurou@gnurou.org:/home/gnurou
ssh gnurou@gnurou.org "cd /srv/http/kanjivg ; rm -Rf currentdata ; tar xfz /home/gnurou/currentdata.tar.gz ; rm /home/gnurou/currentdata.tar.gz"

