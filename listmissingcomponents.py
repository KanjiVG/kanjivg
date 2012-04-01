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

import os, codecs, xml.sax
from kanjivg import *

def addComponents(strokegr, compSet):
	if strokegr.element: compSet.add(strokegr.element)
	if strokegr.original: compSet.add(strokegr.original)
	for child in strokegr.childs:
		if isinstance(child, StrokeGr):
			addComponents(child, compSet)
		

if __name__ == "__main__":
	# Read all kanjis
	handler = KanjisHandler()
	xml.sax.parse("kanjivg.xml", handler)
	kanjis = handler.kanjis.values()

	kanjis.sort(lambda x,y: cmp(x.id, y.id))

	componentsList = set()
	for kanji in kanjis:
		addComponents(kanji.root, componentsList)
	print len(componentsList)

	missingComponents = set()
	for component in componentsList:
		key = hex(realord(component))[2:]
		if not handler.kanjis.has_key(key): missingComponents.add(component)
	print "Missing components:"
	for component in missingComponents:
		print component, hex(realord(component))
	print len(missingComponents), "missing components"
