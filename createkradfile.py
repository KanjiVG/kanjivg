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

def getComponents(group, isRoot = False):
	ret = []
	if not isRoot:
		if group.original: ret.append(group.original)
		elif group.element: ret.append(group.element)
	for child in group.childs:
		if isinstance(child, StrokeGr): ret += getComponents(child)
	return ret

if __name__ == "__main__":
	outFile = codecs.open("kanjiscomponents.txt", "w", "utf-8")
	for line in licenseString.split('\n'):
		outFile.write("# %s\n" % (line))
	outFile.write("""#
# This file gives, for every kanji, the list of its components. Its format is 
# similar to the one of kradfile, with the exception that encoding is utf-8.
# A component is a grapheme that is part of a kanji, without regard about
# whether it is a radical or not. Components are given in their drawing order
# and appear as many times as they are present in the kanji.\n""")

	# Read all kanjis
	handler = KanjisHandler()
	xml.sax.parse("kanjivg.xml", handler)
	kanjis = handler.kanjis.values()

	kanjis.sort(lambda x,y: cmp(x.id, y.id))

	for kanji in kanjis:
		components = getComponents(kanji.root, True)
		if len(components) > 0:
			outList = []
			for c in components:
				if c not in outList: outList.append(c)
			outFile.write('%s %s\n' % (kanji.midashi, " ".join(outList)))
