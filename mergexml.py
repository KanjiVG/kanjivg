#!/usr/bin/python2
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

def createSVG(out, kanji):
	out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	out.write("<!-- ")
	out.write(licenseString)
	out.write("\nThis file has been generated on %s, using the latest KanjiVG data to this date." % (datetime.date.today()))
	out.write("\n-->\n\n")
	out.write("""<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [
<!ATTLIST g
xmlns:kanjivg CDATA #FIXED "http://kanjivg.tagaini.net"
kanjivg:element CDATA #IMPLIED
kanjivg:variant CDATA #IMPLIED
kanjivg:partial CDATA #IMPLIED
kanjivg:original CDATA #IMPLIED
kanjivg:part CDATA #IMPLIED
kanjivg:number CDATA #IMPLIED
kanjivg:tradForm CDATA #IMPLIED
kanjivg:radicalForm CDATA #IMPLIED
kanjivg:position CDATA #IMPLIED
kanjivg:radical CDATA #IMPLIED
kanjivg:phon CDATA #IMPLIED >
<!ATTLIST path
xmlns:kanjivg CDATA #FIXED "http://kanjivg.tagaini.net"
kanjivg:type CDATA #IMPLIED >
]>
<svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
""")
#<defs>
    #<marker id="Triangle"
      #viewBox="0 0 10 10" refX="0" refY="5" 
      #markerUnits="strokeWidth"
      #markerWidth="4" markerHeight="3"
      #orient="auto" stroke="none" fill="#ff0000">
      #<path d="M 0 0 L 10 5 L 0 10 z" />
    #</marker>
#</defs>
	kanji.toSVG(out)
	out.write("</svg>\n")

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
	os.mkdir("output")
	os.mkdir("output/SVG")
	os.mkdir("output/SVGMismatch")
	files = os.listdir("XML")
	handled = set()
	metComponents = set()
	for f in files:
		if not f.endswith(".xml"): continue

		kId = f[:-4]
		if "-" in kId: code, variant = kId.split("-")
		else: code, variant = kId, None

		# Parse XML
		descHandler = KanjisHandler(int(code, 16), variant)
		xml.sax.parse(os.path.join("XML", f), descHandler)
		handled.add(kId)

		# Parse SVG
		parser = xml.sax.make_parser()
		svgHandler = KanjiStrokeHandler()
		parser.setContentHandler(svgHandler)
		parser.setFeature(xml.sax.handler.feature_external_ges, False)
		parser.setFeature(xml.sax.handler.feature_external_pes, False)
		svgFile = os.path.join("SVG", kId + ".svg")
		if os.path.exists(svgFile):
			parser.parse(svgFile)

		metComponents = metComponents.union(descHandler.metComponents)

		kanji = descHandler.kanji
		desc = kanji.getStrokes()
		svg = svgHandler.strokes
		# Copy SVG into kanji desc
		for i in range(min(len(desc), len(svg))):
			desc[i].svg = svg[i]

		# Add dummy strokes for SVG orphans
		for i in range(len(desc), len(svg)):
			s = Stroke(kanji.root)
			s.stype = "Missing stroke"
			s.svg = svg[i]
			kanji.root.childs.append(s)

		if len(desc) != len(svg): dst = "SVGMismatch"
		else: dst = "SVG"
		out = codecs.open("output/%s/%s.svg" % (dst, kanji.kId()), "w", "utf-8")
		createSVG(out, kanji)


	# Now parse orphan SVGs (probably just kana and romaji)
	files = os.listdir("SVG")
	for f in files:
		if not f.endswith(".svg"): continue

		kId = f[:-4]
		if "-" in kId: code, variant = kId.split("-")
		else: code, variant = kId, None

		if f[:-4] in handled: continue
		parser = xml.sax.make_parser()
		svgHandler = KanjiStrokeHandler()
		parser.setContentHandler(svgHandler)
		parser.setFeature(xml.sax.handler.feature_external_ges, False)
		parser.setFeature(xml.sax.handler.feature_external_pes, False)
		parser.parse(os.path.join("SVG", f))

		kanji = Kanji(int(code, 16), variant)
		kanji.root = StrokeGr(None)
		for s in svgHandler.strokes:
			stroke = Stroke(kanji.root)
			stroke.svg = s
			kanji.root.childs.append(stroke)
		# TODO merge with upper part - kana and romaji should not be considered mismatched
