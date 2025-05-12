#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011-2013 Alexandre Courbot
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

import sys, os, re, datetime
from kanjivg import licenseString
from utils import open

verbose = False

pathre = re.compile(r'<path .*d="([^"]*)".*/>')

helpString = """Usage: %s <command> [ kanji files ]
Recognized commands:
  split file1 [ file2 ... ]       extract path data into a -paths suffixed file
  merge file1 [ file2 ... ]       merge path data from -paths suffixed file
  release                         create single release file""" % (sys.argv[0],)

def createPathsSVG(f):
	s = open(f, "r", encoding="utf-8").read()
	paths = pathre.findall(s)
	out = open(f[:-4] + "-paths.svg", "w", encoding="utf-8")
	out.write("""<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" []>
<svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">\n""")
	i = 1
	for path in paths:
		out.write('<!--%2d--><path d="%s"/>\n' % (i, path))
		i += 1
	out.write("</svg>")

def mergePathsSVG(f):
	pFile = f[:-4] + "-paths.svg"
	if not os.path.exists(pFile):
		print("%s does not exist!" % (pFile,))
		return
	s = open(pFile, "r", encoding="utf-8").read()
	paths = pathre.findall(s)
	s = open(f, "r", encoding="utf-8").read()
	pos = 0
	while True:
		match = pathre.search(s[pos:])
		if match and len(paths) == 0 or not match and len(paths) > 0:
			print("Paths count mismatch for %s" % (f,))
			return
		if not match and len(paths) == 0:
			break
		s = s[:pos + match.start(1)] + paths[0] + s[pos + match.end(1):]
		pos += match.start(1) + len(paths[0])
		del paths[0]
	open(f, "w", encoding="utf-8").write(s)

def release():
	datadir = "kanji"
	idMatchString = "<g id=\"kvg:StrokePaths_"
	allfiles = os.listdir(datadir)
	files = []
	for f in allfiles:
                # This rejects the variant files by only choosing
                # files with length of 9, for 0abcd.svg style files.
		if len(f) == 9: files.append(f)
	del allfiles
	files.sort()
	
	out = open("kanjivg.xml", "w", encoding='utf8')
	out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	out.write("<!--\n")
	out.write(licenseString)
	out.write("\nThis file was generated on %s from the most recent KanjiVG data." % (datetime.date.today()))
	out.write("\n-->\n")
	out.write("<kanjivg xmlns:kvg='http://kanjivg.tagaini.net'>\n")
	for f in files:
		data = open(os.path.join(datadir, f), encoding='utf8').read()
		data = data.replace("\r\n", "\n")
		data = data[data.find("<svg "):]
		data = data[data.find(idMatchString) + len(idMatchString):]
		kidend = data.find("\"")
		data = "<kanji id=\"kvg:kanji_%s\">" % (data[:kidend],) + data[data.find("\n"):data.find('<g id="kvg:StrokeNumbers_') - 5] + "</kanji>\n"
		out.write(data)
	out.write("</kanjivg>\n")
	out.close()
	if verbose:
		print("%d kanji emitted" % len(files))

actions = {
	"split": (createPathsSVG, 2),
	"merge": (mergePathsSVG, 2),
	"release": (release, 1)
}

if __name__ == "__main__":
	if len(sys.argv) < 2 or sys.argv[1] not in actions.keys() or \
		len(sys.argv) <= actions[sys.argv[1]][1]:
		print(helpString)
		sys.exit(0)

	action = actions[sys.argv[1]][0]
	files = sys.argv[2:]

	if len(files) == 0:
		action()
	else:
		for f in files:
			if not os.path.exists(f):
				print("%s does not exist!" % (f,))
				continue
			action(f)
