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

import os, codecs, xml.sax, xml.sax.handler, re
from kanjisvg import *

class KanjiStrokeHandler(BasicHandler):
	def __init__(self):
		BasicHandler.__init__(self)
		self.kanji = ""
		self.depth = 0
		self.active = False
		self.pathCpt = 0

	def handle_start_path(self, attrs):
		strokeData = attrs["d"]
		strokeData = re.sub("[\n\t ,]+", ",", strokeData)

		self.kanji += strokeData
		if self.kanji != "": self.kanji += ";"

	def handle_start_g(self, attrs):
		if attrs.has_key("id") and attrs["id"] == "Vektorbild": self.active = True
		if self.active:
			if len(self.kanji) != 0 and self.kanji[-2:] != '[,':
				self.kanji += "[,"
			self.depth += 1

	def handle_end_g(self):
		if self.active:
			self.depth -= 1

if __name__ == "__main__":
	outFile = codecs.open("kanjisstrokes.txt", "w", "utf-8")
	for line in licenseString.split('\n'):
		outFile.write("# %s\n" % (line))

	for f in os.listdir("SVG"):
		# Skip variations
		if len(f) > 9: continue
		if not f.endswith(".svg"): continue
		code = int(f[0 : -4], 0x10)
		# Only output kanjis
		if code < 0x4e00 or code > 0x9fbf: continue
		uc = unichr(code)
		outFile.write(uc + " ")

		parser = xml.sax.make_parser()
		handler = KanjiStrokeHandler()
		parser.setContentHandler(handler)
		parser.setFeature(xml.sax.handler.feature_external_ges, False)
		parser.setFeature(xml.sax.handler.feature_external_pes, False)
		parser.parse(os.path.join("SVG", f))
		outFile.write(handler.kanji + "\n")
