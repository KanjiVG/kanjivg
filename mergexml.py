#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009  Alexandre Courbot
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

import os, codecs, xml.sax, re, datetime
from kanjivg import *

class KanjiStrokeHandler(BasicHandler):
	def __init__(self):
		BasicHandler.__init__(self)
		self.strokes = []
		self.active = False

	def handle_start_path(self, attrs):
		strokeData = attrs["d"]
		# Replace spaces between digits by the comma separator
		strokeData = re.sub('(\d) (\d)', '\\1,\\2', strokeData)
		strokeData = re.sub("[\n\t ]+", "", strokeData)

		self.strokes.append(strokeData)

	def handle_start_g(self, attrs):
		if attrs.has_key("id") and attrs["id"] == "Vektorbild": self.active = True

if __name__ == "__main__":
	files = os.listdir("XML")
	kanjis = []
	mismatch = []
	handled = set()
	for f in files:
		# Let's skip the variations out of the process for now...
		if len(f) > 10: continue

		if not f.endswith(".xml"): continue
		descHandler = KanjisHandler()
		xml.sax.parse(os.path.join("XML", f), descHandler)
		handled.add(f[:-4])

		parser = xml.sax.make_parser()
		svgHandler = KanjiStrokeHandler()
		parser.setContentHandler(svgHandler)
		parser.setFeature(xml.sax.handler.feature_external_ges, False)
		parser.setFeature(xml.sax.handler.feature_external_pes, False)
		svgFile = os.path.join("SVG", f[:-3] + "svg")
		if os.path.exists(svgFile):
			parser.parse(svgFile)

		kanji = descHandler.kanjis.values()[0]
		desc = kanji.getStrokes()
		svg = svgHandler.strokes
		if len(desc) != len(svg): mismatch.append((descHandler.kanjis.values()[0].root.element, len(desc), len(svg)))
		for i in range(min(len(desc), len(svg))):
			desc[i].svg = svg[i]
		# Add dummy strokes for SVG orphans
		for i in range(len(desc), len(svg)):
			s = Stroke()
			s.stype = "Missing stroke"
			s.svg = svg[i]
			kanji.root.childs.append(s)
		kanjis.append(kanji)

	# Now parse orphan SVGs (probably just kanas and romanjis)
	files = os.listdir("SVG")
	for f in files:
		# Let's skip the variations out of the process for now...
		if len(f) > 10: continue

		if not f.endswith(".svg"): continue
		if f[:-4] in handled: continue
		parser = xml.sax.make_parser()
		svgHandler = KanjiStrokeHandler()
		parser.setContentHandler(svgHandler)
		parser.setFeature(xml.sax.handler.feature_external_ges, False)
		parser.setFeature(xml.sax.handler.feature_external_pes, False)
		parser.parse(os.path.join("SVG", f))

		kanji = Kanji(f[:-4])
		kanji.midashi = unichr(int(f[:-4], 16))
		kanji.root = StrokeGr(None)
		for s in svgHandler.strokes:
			stroke = Stroke()
			stroke.svg = s
			kanji.root.childs.append(stroke)
		kanjis.append(kanji)

	mismatch.sort()
	misout = codecs.open("wiki.d/Main.StrokeCountMismatch", "w", "utf-8")
	misout.write('version=pmwiki-2.1.0 urlencoded=1\ntext=')
	misout.write("'''This page is generated - please do not edit it!'''%0a%0aThe following kanjis have a stroke order mismatch between their XML and SVG descriptions:%0a")
	for i in range(len(mismatch)):
		misout.write("* %s: XML %d, SVG %d" % (mismatch[i][0], mismatch[i][1], mismatch[i][2]))
		misout.write("%0a")
		#print "%s: %5d %5d" % (mismatch[i][0], mismatch[i][1], mismatch[i][2])
	kanjis.sort(lambda x,y: cmp(x.id, y.id))

	out = codecs.open("kanjivg.xml", "w", "utf-8")
	out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	out.write("<!-- ")
	out.write(licenseString)
	out.write("\nThis file has been generated on %s, using the latest KanjiVG data to this date." % (datetime.date.today()))
	out.write("\n-->\n\n")
	out.write("<kanjis>\n");
	for kanji in kanjis:
		kanji.toXML(out)
	out.write("</kanjis>\n");

