#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#
#  Copyright (C) 2023 Sebastian Grygiel
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
from kanjivg import Stroke, StrokeGr
from utils import listSvgFiles, readXmlFile, canonicalId, PYTHON_VERSION_MAJOR

if PYTHON_VERSION_MAJOR > 2:
	def unicode(s):
		return s
	def unichr(c):
		return chr(c)

helpString = """Usage: %s <find-svg|find-xml> <element1> [...elementN]

Recognized commands:
  find-svg      Find and view summary of an SVG file for the given 
                element in ./kanji/ directory.
  find-xml      Find and view summary of a <kanji> entry for
                the given element from ./kanjivg.xml file.

Parameters:
  element       May either be the singular character, e.g. 並 or its
                unicode code-point e.g. 4e26.

Examples:
  %s find-svg 並      Will list SVG files describing given character.
  %s find-xml 4e26    Will list <kanji> entry for the same character.
""" % (sys.argv[0], sys.argv[0], sys.argv[0])

# Output helper

lossInWeirdEncoding = False
def writeOutput(data, output):
	if PYTHON_VERSION_MAJOR >= 3:
		output.write(data)
		return
	
	global lossInWeirdEncoding
	if output.encoding == None:
		encoding = 'utf8'
	else:
		encoding = output.encoding

	encoded = data.encode(encoding, errors="replace")
	if encoding != 'utf8' and encoding != 'utf-8':
		if encoded.decode(encoding) != data:
			lossInWeirdEncoding = encoding
	
	output.write(encoded)

# Summary generators

def strokeGroupSummary(gr, indent = 0):
	if not isinstance(gr, StrokeGr):
		raise Exception("Invalid structure")
	
	ret = unicode(" " * indent * 4)
	# ret += gr.element if gr.element is not None and len(gr.element) > 0 else "・"
	ret += "- group"
	if gr.element is not None and len(gr.element) > 0:
		ret += " %s" % (gr.element,)
	if gr.position:
		ret += " (%s)" % (gr.position,)

	childStrokes = [s.stype for s in gr.childs if isinstance(s, Stroke) and s.stype]
	if len(childStrokes):
		ret += "\n%s- strokes: %s" % (" " * (indent+1) * 4, ' '.join(childStrokes))

	ret += "\n"

	for g in gr.childs:
		if isinstance(g, StrokeGr):
			ret += strokeGroupSummary(g, indent + 1)

	return ret

def characterSummary(c):
	ret = "Character summary: %s (%s)" % (c.code, c.strokes.element)
	if c.variant:
		ret += " - variant: %s" % (c.variant)
	ret += "\n"
	ret += strokeGroupSummary(c.strokes)
	return ret

# Commands

def commandFindSvg(arg):
	id = canonicalId(arg)
	kanji = [(f.path, f.read()) for f in listSvgFiles("./kanji/") if f.id == id]
	print("Found %d files matching ID %s" % (len(kanji), id))
	for i, (path, c) in enumerate(kanji):
		print("\nFile %s (%d/%d):" % (path, i+1, len(kanji)))
		writeOutput(characterSummary(c) + "\n", sys.stdout)

def commandFindXml(arg):
	id = canonicalId(arg)
	files = readXmlFile('./kanjivg.xml')
	if id in files:
		writeOutput(characterSummary(files[id]) + "\n", sys.stdout)
	else:
		writeOutput(unicode("Character %s (%s) not found.\n") % (id, unichr(int(id, 16))), sys.stdout)

# Main wrapper

actions = {
	"find-svg": (commandFindSvg, 2),
	"find-xml": (commandFindXml, 2),
}

if __name__ == "__main__":
	if len(sys.argv) < 2 or sys.argv[1] not in actions.keys() or \
		len(sys.argv) <= actions[sys.argv[1]][1]:
		print(helpString)
		sys.exit(0)

	action = actions[sys.argv[1]][0]
	args = sys.argv[2:]

	if len(args) == 0:
		action()
	else:
		for f in args:
			action(f)
	
	if lossInWeirdEncoding:
		notice = """\nNotice: SOME CHARACTERS IN THE OUTPUT HAVE BEEN REPLACED WITH QUESTION MARKS.
        The text output has been encoded using your encoding of the standard
        output (%s). Try redirecting output to file if you can't get it to
        work in terminal. e.g.: kvg-lookup.py find-svg 4e26 > output.txt\n""" % (lossInWeirdEncoding,)
		writeOutput(notice, sys.stderr)
