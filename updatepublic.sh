#!/bin/sh
rm -f kanjivg.xml.gz
./mergexml.py
gzip kanjivg.xml
scp kanjivg.xml.gz gnurou@gnurou.org:/srv/http/kanjivg/upload/Main/kanjivg-latest.xml.gz
ssh gnurou@gnurou.org "cd /srv/http/kanjivg.git ; zcat /srv/http/kanjivg/upload/Main/kanjivg-latest.xml.gz >kanjivg.xml ; ./createsvgfiles.py"

