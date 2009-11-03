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

import os, codecs, xml.sax
from kanjivg import *

def getRadicals(group):
	ret = []
	if group.radical:
		elt = group.element
		if elt: ret = [ elt ]
	for child in group.childs:
		if isinstance(child, StrokeGr): ret += getRadicals(child)
	return ret

if __name__ == "__main__":
	outFile = codecs.open("kanjisradicals.txt", "w", "utf-8")
	for line in licenseString.split('\n'):
		outFile.write("# %s\n" % (line))
	outFile.write("""#
# This file gives, for every kanji, the list of its radicals. Its format is 
# similar to the one of kradfile, with the exception that encoding is utf-8.\n""")

	# Read all kanjis
	kanjis = []
	for f in os.listdir("XML"):
		# Skip variants
		if len(f) > 9: continue
		if not f.endswith(".xml"): continue
		kanjiDescFile = "XML/" + f
		handler = KanjisHandler()
		xml.sax.parse(kanjiDescFile, handler)
		kanjis += handler.kanjis.values()

	kanjis.sort(lambda x,y: cmp(x.id, y.id))

	radkanjis = {}
	for kanji in kanjis:
		radicals = []
		for child in kanji.root.childs:
			if isinstance(child, StrokeGr):
				radicals += getRadicals(child)
		for radical in radicals:
			if radkanjis.has_key(radical):
				radkanjis[radical].add(kanji.midashi)
			else:
				s = set()
				s.add(kanji.midashi)
				radkanjis[radical] = set(s)
	for rad in radkanjis.keys():
		if len(rad) > 0:
			outFile.write('%s %s\n' % (rad, " ".join(radkanjis[rad])))
