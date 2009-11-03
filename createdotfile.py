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

import sys, os, codecs, xml.sax
from kanjivg import *

def getChildsList(group):
	ret = [ child for child in group.childs if isinstance(child, StrokeGr) ]
	i = 0
	while i < len(ret):
		child = ret[i]
		if not child.original and not child.element:
			ret[i:i+1] = [ c for c in child.childs if isinstance(c, StrokeGr)]
			allElts = False
		else: i += 1
	return ret

def getComponents(group):
	toProcess = getChildsList(group)
	level = 0
	ret = [ ]
	alreadyDone = [ ]
	while toProcess:
		ret.append(str(level))
		nextLevel = []
		appended = False
		for next in toProcess:
			elt = next.original
			if not elt: elt = next.element
			if elt and not elt in alreadyDone: 
				appended = True
				ret.append(elt)
				alreadyDone.append(elt)
			nextLevel += getChildsList(next)
		if not appended:
			ret = ret[0:-1]
		else: level += 1
		toProcess = nextLevel
	return ret

if __name__ == "__main__":
	upKanjis = set()
	upKanjis.add(u'白')
	upKanjis.add(u'羽')
	upKanjis.add(u'竹')

	outFile = codecs.open("kanjisgraph.dot", "w", "utf-8")
	outFile.write("digraph kanjis {\n")

	# Read all kanjis
	kanjis = []
	for f in os.listdir("XML"):
		# Skip variants
		if len(f) > 9: continue
		if not f.endswith(".xml"): continue
		handler = KanjisHandler()
		xml.sax.parse("XML/" + f, handler)
		kanjis += handler.kanjis.values()

	kanjis.sort(lambda x,y: cmp(x.id, y.id))

	nodes = set()
	graphs = set()
	while len(upKanjis) > 0:
		nextKanjis = set()
		for kanji in kanjis:
			components = [ child for child in kanji.root.childs if isinstance(child, StrokeGr) ]
			for c in components:
				if c.original: left = c.original
				else: left = c.element
				if kanji.root.original: right = kanji.root.original
				else: right = kanji.root.element
				if not left or not right: continue
				if not left in upKanjis: continue
				if ord(left) > 0xffff or ord(right) > 0xffff: continue
				nextKanjis.add(right)
				nodes.add(left)
				nodes.add(right)
				graphs.add((left, right))
		upKanjis = nextKanjis

	for node in nodes:
		outFile.write('\tnode_%x [label="%s"];\n' % (ord(node), node))
	outFile.write('\n')
	for (left, right) in graphs:
		outFile.write('\tnode_%x -> node_%x;\n' % (ord(left), ord(right)))
	outFile.write("}\n")
