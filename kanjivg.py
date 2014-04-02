# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2013 Alexandre Courbot
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

from xmlhandler import *

# Sample licence header
licenseString = """Copyright (C) 2009-2013 Ulrich Apel.
This work is distributed under the conditions of the Creative Commons
Attribution-Share Alike 3.0 Licence. This means you are free:
* to Share - to copy, distribute and transmit the work
* to Remix - to adapt the work

Under the following conditions:
* Attribution. You must attribute the work by stating your use of KanjiVG in
  your own copyright header and linking to KanjiVG's website
  (http://kanjivg.tagaini.net)
* Share Alike. If you alter, transform, or build upon this work, you may
  distribute the resulting work only under the same or similar license to this
  one.

See http://creativecommons.org/licenses/by-sa/3.0/ for more details."""

def isKanji(v):
	return (v >= 0x4E00 and v <= 0x9FC3) or (v >= 0x3400 and v <= 0x4DBF) or (v >= 0xF900 and v <= 0xFAD9) or (v >= 0x2E80 and v <= 0x2EFF) or (v >= 0x20000 and v <= 0x2A6DF)

# Returns the unicode of a character in a unicode string, taking surrogate pairs into account
def realord(s, pos = 0):
	if s == None: return None
	code = ord(s[pos])
	if code >= 0xD800 and code < 0xDC00:
		if (len(s) <= pos + 1):
			print "realord warning: missing surrogate character"
			return 0
		code2 = ord(s[pos + 1])
		if code2 >= 0xDC00 and code < 0xE000:
			code = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)	
	return code

def realchr(i):
	if i < 0x10000: return unichr(i)
	else: return unichr(((i - 0x10000) >> 10) + 0xD800) + unichr(0xDC00 + (i & 0x3ff))

class Kanji:
	"""Describes a kanji. The root stroke group is accessible from the strokes member."""
	def __init__(self, code, variant):
		# Unicode of char being represented (int)
		self.code = code
		# Variant of the character, if any
		self.variant = variant
		self.strokes = None

	# String identifier used to uniquely identify the kanji
	def kId(self):
		ret = "%05x" % (self.code,)
		if self.variant: ret += "-%s" % (self.variant,)
		return ret

	def outputStrokesNumbers(self, out, indent = 0):
		strokes = self.getStrokes()
		cpt = 1
		for stroke in strokes:
			stroke.numberToSVG(out, cpt, indent + 1)
			cpt += 1

	def outputStrokes(self, out, indent = 0):
		self.strokes.toSVG(out, self.kId(), [0], [1])

	def simplify(self):
		self.strokes.simplify()

	def getStrokes(self):
		return self.strokes.getStrokes()


class StrokeGr:
	"""Describes a stroke group belonging to a kanji as closely as possible to the XML format. Sub-stroke groups or strokes are available in the childs member. They can either be of class StrokeGr or Stroke so their type should be checked."""
	def __init__(self, parent):
		self.parent = parent
		if parent: parent.childs.append(self)
		# Element of strokegr
		self.element = None
		# A more common, safer element this one derives of
		self.original = None
		self.part = None
		self.number = None
		self.variant = False
		self.partial = False
		self.tradForm = False
		self.radicalForm = False
		self.position = None
		self.radical = None
		self.phon = None
		
		self.childs = []

	def toSVG(self, out, rootId, groupCpt = [0], strCpt = [1], indent = 0):
		gid = rootId
		if groupCpt[0] != 0: gid += "-g" + str(groupCpt[0])
		groupCpt[0] += 1

		idString = ' id="kvg:%s"' % (gid)
		eltString = ""
		if self.element: eltString = ' kvg:element="%s"' % (self.element)
		variantString = ""
		if self.variant: variantString = ' kvg:variant="true"'
		partialString = ""
		if self.partial: partialString = ' kvg:partial="true"'
		origString = ""
		if self.original: origString = ' kvg:original="%s"' % (self.original)
		partString = ""
		if self.part: partString = ' kvg:part="%d"' % (self.part)
		numberString = ""
		if self.number: numberString = ' kvg:number="%d"' % (self.number)
		tradFormString = ""
		if self.tradForm: tradFormString = ' kvg:tradForm="true"'
		radicalFormString = ""
		if self.radicalForm: radicalFormString = ' kvg:radicalForm="true"'
		posString = ""
		if self.position: posString = ' kvg:position="%s"' % (self.position)
		radString = ""
		if self.radical: radString = ' kvg:radical="%s"' % (self.radical)
		phonString = ""
		if self.phon: phonString = ' kvg:phon="%s"' % (self.phon)
		out.write("\t" * indent + '<g%s%s%s%s%s%s%s%s%s%s%s%s>\n' % (idString, eltString, partString, numberString, variantString, origString, partialString, tradFormString, radicalFormString, posString, radString, phonString))

		for child in self.childs:
			child.toSVG(out, rootId, groupCpt, strCpt, indent + 1)

		out.write("\t" * indent + '</g>\n')


	def components(self, simplified = True, recursive = False, level = 0):
		ret = []
		childsComp = []
		for child in self.childs:
			if isinstance(child, StrokeGr):
				found = False
				# Can we find the component in the child?
				if simplified and child.original: ret.append(child.original); found = True
				elif child.element: ret.append(child.element); found = True
				# If not, the components we are looking for are the child's
				# components - we also do that if we asked all the sub-components of the group
				if not found or recursive:
					newLevel = level
					if found: newLevel += 1
					childsComp += child.components(simplified, recursive, newLevel)
		if recursive and not len(ret) == 0: ret = [ level ] + ret + childsComp
		return ret

	def simplify(self):
		for child in self.childs: 
			if isinstance(child, StrokeGr): child.simplify()
		if len(self.childs) == 1 and isinstance(self.childs[0], StrokeGr):
			# Check if there is no conflict
			if child.element and self.element and child.element != self.element: return
			if child.original and self.original and child.original != self.original: return
			# Parts cannot be merged
			if child.part and self.part and self.part != child.part: return
			if child.variant and self.variant and child.variant != self.variant: return
			if child.partial and self.partial and child.partial != self.partial: return
			if child.tradForm and self.tradForm and child.tradForm != self.tradForm: return
			if child.radicalForm and self.radicalForm and child.radicalForm != self.radicalForm: return
			# We want to preserve inner identical positions - we may have something at the top
			# of another top element, for instance.
			if child.position and self.position: return
			if child.radical and self.radical and child.radical != self.radical: return
			if child.phon and self.phon and child.phon != self.phon: return

			# Ok, let's merge!
			child = self.childs[0]
			self.childs = child.childs
			if child.element: self.element = child.element
			if child.original: self.original = child.original
			if child.part: self.part = child.part
			if child.variant: self.variant = child.variant
			if child.partial: self.partial = child.partial
			if child.tradForm: self.tradForm = child.tradForm
			if child.radicalForm: self.radicalForm = child.radicalForm
			if child.position: self.position = child.position
			if child.radical: self.radical = child.radical
			if child.phon: self.phon = child.phon

	def getStrokes(self):
		ret = []
		for child in self.childs: 
			if isinstance(child, StrokeGr): ret += child.getStrokes()
			else: ret.append(child)
		return ret
		

class Stroke:
	"""A single stroke, containing its type and (optionally) its SVG data."""
	def __init__(self, parent):
		self.stype = None
		self.svg = None
		self.numberPos = None
	
	def numberToSVG(self, out, number, indent = 0):
		if self.numberPos:
			out.write("\t" * indent + '<text transform="matrix(1 0 0 1 %.2f %.2f)">%d</text>\n' % (self.numberPos[0], self.numberPos[1], number)) 

	def toSVG(self, out, rootId, groupCpt, strCpt, indent = 0):
		pid = rootId + "-s" + str(strCpt[0])
		strCpt[0] += 1
		s = "\t" * indent + '<path id="kvg:%s"' % (pid,)
		if self.stype: s += ' kvg:type="%s"' % (self.stype,)
		if self.svg: s += ' d="%s"' % (self.svg)
		s += '/>\n'
		out.write(s)

class KanjisHandler(BasicHandler):
	"""XML handler for parsing kanji files. It can handle single-kanji files or aggregation files. After parsing, the kanjis are accessible through the kanjis member, indexed by their svg file name."""
	def __init__(self, code, variant):
		BasicHandler.__init__(self)
		self.kanji = Kanji(code, variant)
		self.groups = []
		self.compCpt = {}
		self.metComponents = set()

	def handle_start_kanji(self, attrs):
		pass

	def handle_end_kanji(self):
		if len(self.groups) != 0:
			print "WARNING: stroke groups remaining after reading kanji!"
		self.groups = []

	def handle_start_strokegr(self, attrs):
		if len(self.groups) == 0: parent = None
		else: parent = self.groups[-1]
		group = StrokeGr(parent)

		# Now parse group attributes
		if attrs.has_key("element"): group.element = unicode(attrs["element"])
		if attrs.has_key("variant"): group.variant = str(attrs["variant"])
		if attrs.has_key("partial"): group.partial = str(attrs["partial"])
		if attrs.has_key("original"): group.original = unicode(attrs["original"])
		if attrs.has_key("part"): group.part = int(attrs["part"])
		if attrs.has_key("number"): group.number = int(attrs["number"])
		if attrs.has_key("tradForm") and str(attrs["tradForm"]) == "true": group.tradForm = True
		if attrs.has_key("radicalForm") and str(attrs["radicalForm"]) == "true": group.radicalForm = True
		if attrs.has_key("position"): group.position = unicode(attrs["position"])
		if attrs.has_key("radical"): group.radical = unicode(attrs["radical"])
		if attrs.has_key("phon"): group.phon = unicode(attrs["phon"])

		self.groups.append(group)

		if group.element: self.metComponents.add(group.element)
		if group.original: self.metComponents.add(group.original)

		if group.number:
			if not group.part: print "%s: Number specified, but part missing" % (self.kanji.kId())
			# The group must exist already
			if group.part > 1:
				if not self.compCpt.has_key(group.element + str(group.number)):
					print "%s: Missing numbered group" % (self.kanji.kId())
				elif self.compCpt[group.element + str(group.number)] != group.part - 1:
					print "%s: Incorrectly numbered group" % (self.kanji.kId())
			# The group must not exist
			else:
				if self.compCpt.has_key(group.element + str(group.number)):
					print "%s: Duplicate numbered group" % (self.kanji.kId())
			self.compCpt[group.element + str(group.number)] = group.part
		# No number, just a part - groups restart with part 1, otherwise must
		# increase correctly
		elif group.part:
				# The group must exist already
			if group.part > 1:
				if not self.compCpt.has_key(group.element):
					print "%s: Incorrectly started multi-part group" % (self.kanji.kId())
				elif self.compCpt[group.element] != group.part - 1:
					print "%s: Incorrectly splitted multi-part group" % (self.kanji.kId())
			self.compCpt[group.element] = group.part

	def handle_end_strokegr(self):
		group = self.groups.pop()
		if len(self.groups) == 0:
			if self.kanji.strokes:
				print "WARNING: overwriting root of kanji!"
			self.kanji.strokes = group

	def handle_start_stroke(self, attrs):
		if len(self.groups) == 0: parent = None
		else: parent = self.groups[-1]
		stroke = Stroke(parent)
		stroke.stype = unicode(attrs["type"])
		if attrs.has_key("path"): stroke.svg = unicode(attrs["path"])
		self.groups[-1].childs.append(stroke)

class SVGHandler(BasicHandler):
	"""SVG handler for parsing final kanji files. It can handle single-kanji files or aggregation files. After parsing, the kanji are accessible through the kanjis member, indexed by their svg file name."""
	def __init__(self):
		BasicHandler.__init__(self)
		self.kanjis = {}
		self.currentKanji = None
		self.groups = []
		self.metComponents = set()

	def handle_start_g(self, attrs):
		# Special case for handling the root
		if len(self.groups) == 0:
			id = hex(realord(attrs["kvg:element"]))[2:]
			self.currentKanji = Kanji(id)
			self.kanjis[id] = self.currentKanji
			self.compCpt = {}
			parent = None
		else: parent = self.groups[-1]
	
		group = StrokeGr(parent)
		# Now parse group attributes
		if attrs.has_key("kvg:element"): group.element = unicode(attrs["kvg:element"])
		if attrs.has_key("kvg:variant"): group.variant = str(attrs["kvg:variant"])
		if attrs.has_key("kvg:partial"): group.partial = str(attrs["kvg:partial"])
		if attrs.has_key("kvg:original"): group.original = unicode(attrs["kvg:original"])
		if attrs.has_key("kvg:part"): group.part = int(attrs["kvg:part"])
		if attrs.has_key("kvg:number"): group.number = int(attrs["kvg:number"])
		if attrs.has_key("kvg:tradForm") and str(attrs["kvg:tradForm"]) == "true": group.tradForm = True
		if attrs.has_key("kvg:radicalForm") and str(attrs["kvg:radicalForm"]) == "true": group.radicalForm = True
		if attrs.has_key("kvg:position"): group.position = unicode(attrs["kvg:position"])
		if attrs.has_key("kvg:radical"): group.radical = unicode(attrs["kvg:radical"])
		if attrs.has_key("kvg:phon"): group.phon = unicode(attrs["kvg:phon"])

		self.groups.append(group)

		if group.element: self.metComponents.add(group.element)
		if group.original: self.metComponents.add(group.original)

		if group.number:
			if not group.part: print "%s: Number specified, but part missing" % (self.currentKanji.kId())
			# The group must exist already
			if group.part > 1:
				if not self.compCpt.has_key(group.element + str(group.number)):
					print "%s: Missing numbered group" % (self.currentKanji.kId())
				elif self.compCpt[group.element + str(group.number)] != group.part - 1:
					print "%s: Incorrectly numbered group" % (self.currentKanji.kId())
			# The group must not exist
			else:
				if self.compCpt.has_key(group.element + str(group.number)):
					print "%s: Duplicate numbered group" % (self.currentKanji.kId())
			self.compCpt[group.element + str(group.number)] = group.part
		# No number, just a part - groups restart with part 1, otherwise must
		# increase correctly
		elif group.part:
				# The group must exist already
			if group.part > 1:
				if not self.compCpt.has_key(group.element):
					print "%s: Incorrectly started multi-part group" % (self.currentKanji.kId())
				elif self.compCpt[group.element] != group.part - 1:
					print "%s: Incorrectly splitted multi-part group" % (self.currentKanji.kId())
			self.compCpt[group.element] = group.part

	def handle_end_g(self):
		group = self.groups.pop()
		# End of kanji?
		if len(self.groups) == 0:
			self.currentKanji.strokes = group
			self.currentKanji = None
			self.groups = []


	def handle_start_path(self, attrs):
		if len(self.groups) == 0: parent = None
		else: parent = self.groups[-1]
		stroke = Stroke(parent)
		stroke.stype = unicode(attrs["kvg:type"])
		if attrs.has_key("d"): stroke.svg = unicode(attrs["d"])
		self.groups[-1].childs.append(stroke)
