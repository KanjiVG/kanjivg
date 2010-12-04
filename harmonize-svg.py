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
from xml.etree.ElementTree import XMLID, tostring
import re, codecs, os, string, kanjivg, os.path, sys

def findText(elt):
	if elt.text: return elt.text
	else:
		childs = elt.getchildren()
		if len(childs): return findText(childs[0])
		else: return None

class Parser:
	def __init__(self, content):
		self.content = content

	def parse(self):
		while 1:
			match = re.search('\$\$(\w*)', self.content)
			if not match: break
			fname = 'callback_' + match.group(1)
			if hasattr(self, fname):
				rfunc = getattr(self, fname)
				ret = rfunc()
				self.content = self.content[:match.start(0)] + ret + self.content[match.end(0):]
			else: self.content = self.content[:match.start(0)] + self.content[match.end(0):]

class TemplateParser(Parser):
	def __init__(self, content, kanji, document, groups):
		Parser.__init__(self, content)
		self.kanji = kanji
		self.document = document
		self.groups = groups

	def callback_kanji(self):
		return self.kanji

	def callback_strokenumbers(self):
		if not self.groups.has_key("StrokeNumbers"):
			print "Error - no StrokeNumbers group for kanji %s (%s)" % (self.kanji, hex(kanjivg.realord(self.kanji)))
			return ""
		numbers = self.groups["StrokeNumbers"]
		elts = numbers.findall(".//{http://www.w3.org/2000/svg}text")
		strs = []
		for elt in elts:
			attrs = []
			if elt.attrib.has_key("transform"): attrs.append(' transform="%s"' % (elt.attrib["transform"],))
			if elt.attrib.has_key("x"): attrs.append(' x="%s"' % (elt.attrib["x"],))
			if elt.attrib.has_key("y"): attrs.append(' y="%s"' % (elt.attrib["y"],))
			strs.append('<text%s>%s</text>' % (''.join(attrs), findText(elt)))
		return "\n\t\t".join(strs)

	def callback_strokepaths(self):
		if not self.groups.has_key("StrokePaths"):
			print "Error - no StrokePaths group for kanji %s (%s)" % (self.kanji, hex(kanjivg.realord(self.kanji)))
			return ""
		paths = self.groups["StrokePaths"]
		elts = paths.findall(".//{http://www.w3.org/2000/svg}path")
		strs = []
		for elt in elts:
			d = elt.attrib["d"]
			d = re.sub('(\d) (\d)', '\\1,\\2', d)
			d = re.sub("[\n\t ]+", "", d)
			strs.append('<path d="%s"/>' % (d,))
		return "\n\t\t".join(strs)

if __name__ == "__main__":
	# Only process files given as argument...
	if len(sys.argv) > 1:
		filesToProceed = sys.argv[1:]
	# Or do the whole SVG set if no argument is given
	else:
		filesToProceed = []
		for f in os.listdir("SVG"):
			if not f.endswith(".svg"): continue
			filesToProceed.append(os.path.join("SVG", f))

	for f in filesToProceed:
		fname = f.split(os.path.sep)[-1]
		if fname[4] in "0123456789abcdef":
			kanji = kanjivg.realchr(int(fname[:5], 16))
		else: kanji = kanjivg.realchr(int(fname[:4], 16))

		document, groups = XMLID(open(f).read())
		tpp = TemplateParser(open("template.svg").read(), kanji, document, groups)
		tpp.parse()
		out = codecs.open(f, "w", "utf-8")
		out.write(tpp.content)
