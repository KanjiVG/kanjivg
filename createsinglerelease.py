#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011  Alexandre Courbot
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Take all the individual SVG files and merge them into a single file suitable
# for release. This file only includes non-variant kanji.

import os, datetime, re
from kanjivg import licenseString

__datadir = "kanji"
__idMatchString = "<g id=\"kvg:StrokePaths_"

if __name__ == "__main__":
	allfiles = os.listdir(__datadir)
	files = []
	for f in allfiles:
		if len(f) == 9: files.append(f)
	del allfiles
	files.sort()
	
	out = open("kanjivg.xml", "w")
	out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	out.write("<!--\n")
	out.write(licenseString)
	out.write("\nThis file has been generated on %s, using the latest KanjiVG data\nto this date." % (datetime.date.today()))
	out.write("\n-->\n")
	out.write("<kanjivg>\n")
	for f in files:
		data = open(os.path.join(__datadir, f)).read()
		data = data[data.find("<svg "):]
		data = data[data.find(__idMatchString) + len(__idMatchString):]
		kidend = data.find("\"")
		data = "<kanji id=\"kvg:kanji_%s\">" % (data[:kidend],) + data[data.find("\n"):data.find('<g id="kvg:StrokeNumbers_') - 5] + "</kanji>\n"
		out.write(data)
	out.write("</kanjivg>\n")
	out.close()
	print("%d kanji emitted" % len(files))
