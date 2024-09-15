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
from utils import PYTHON_VERSION_MAJOR, canonicalId

if PYTHON_VERSION_MAJOR > 2:
	def unicode(s):
		return s

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

# Returns the unicode of a character in a unicode string, taking
# surrogate pairs into account

# Why do we need to worry about surrogate pairs? This doesn't occur in
# KanjiVG.

def realord(s, pos = 0):
	if s == None: return None
	code = ord(s[pos])
	if code >= 0xD800 and code < 0xDC00:
		if (len(s) <= pos + 1):
			print("realord warning: missing surrogate character")
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
	def __init__(self, code, variant = None):
		# Unicode of char being represented (standard str)
		self.code = canonicalId(code)
		# Variant of the character, if any
		self.variant = variant
		self.strokes = None

	def __repr__(self):
		return repr(vars(self))

	# String identifier used to uniquely identify the kanji
	def kId(self):
		ret = self.code
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
	def __init__(self, parent = None):
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
		self.ID = None

		self.childs = []

	def __repr__(self):
		return repr(vars(self))

	def setParent(self, parent):
		if self.parent is not None or parent is None:
			raise "Set parent should only be set once! There is no cleanup for old parents."
		parent.childs.append(self)
		self.parent = parent

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
		
	def __repr__(self):
		return repr(vars(self))
	
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
	def __init__(self):
		BasicHandler.__init__(self)
		self.kanji = None
		self.kanjis = {}
		self.group = None
		self.groups = []
		# This stores the components for checking
		self.compCpt = {}
		self.metComponents = set()

	def handle_start_kanji(self, attrs):
		if self.kanji is not None:
			raise Exception("Kanji cannot be nested")
		if self.group is not None:
			raise Exception("Kanji cannot be inside a group")
		if len(self.groups) != 0:
			raise Exception("Previous kanji not closed correctly")
		idType, idVariantStr = str(attrs["id"]).split("_")
		if idType != "kvg:kanji":
			raise Exception("Each kanji should have id formatted as kvg:kanji_XXXXX.")
		idVariant = idVariantStr.split('-')
		self.kanji = Kanji(*idVariant)
		self.compCpt = {}

	def handle_end_kanji(self):
		if self.group is not None:
			raise Exception("A group is not closed inside the kanji.")
		if len(self.groups) != 1:
			raise Exception("Kanji should have 1 root group.")
		self.kanji.strokes = self.groups[0]
		self.kanjis[self.kanji.code] = self.kanji
		self.groups = []
		self.kanji = None

	def handle_start_g(self, attrs):
		if self.kanji is None:
			raise Exception("Stroke group must be inside a kanji")
		group = StrokeGr(self.group)

		# Now parse group attributes
		if "kvg:element" in attrs: group.element = unicode(attrs["kvg:element"])
		if "kvg:variant" in attrs: group.variant = str(attrs["kvg:variant"])
		if "kvg:partial" in attrs: group.partial = str(attrs["kvg:partial"])
		if "kvg:original" in attrs: group.original = unicode(attrs["kvg:original"])
		if "kvg:part" in attrs: group.part = int(attrs["kvg:part"])
		if "kvg:number" in attrs: group.number = int(attrs["kvg:number"])
		if "kvg:tradForm" in attrs and str(attrs["kvg:tradForm"]) == "true": group.tradForm = True
		if "kvg:radicalForm" in attrs and str(attrs["kvg:radicalForm"]) == "true": group.radicalForm = True
		if "kvg:position" in attrs: group.position = unicode(attrs["kvg:position"])
		if "kvg:radical" in attrs: group.radical = unicode(attrs["kvg:radical"])
		if "kvg:phon" in attrs: group.phon = unicode(attrs["kvg:phon"])

		group.ID = str(attrs["id"])
		self.group = group

		if group.element: self.metComponents.add(group.element)
		if group.original: self.metComponents.add(group.original)

		if group.number:
			if not group.part:
				print("%s: group %s has number %d, but no part" % (self.kanji.kId(), group.ID, group.number))
			ged = group.element + "n" + str(group.number)
			# The group must exist already
			if group.part > 1:
				if (ged) not in self.compCpt:
					print("%s: Numbered group %s with no first part" % (self.kanji.kId(), group.ID))
				elif self.compCpt[ged] != group.part - 1:
					print("%s: Incorrectly numbered group" % (self.kanji.kId()))
			# The group must not exist
			else:
				if (ged) in self.compCpt:
					if self.compCpt[ged] == group.part:
						print("%s: Duplicate group %s %s for %s part %d - %d" % (self.kanji.kId(), group.ID, ged,group.element, group.part, group.number))
			self.compCpt[ged] = group.part
		# No number, just a part - groups restart with part 1, otherwise must
		# increase correctly
		elif group.part:
				# The group must exist already
			if group.part > 1:
				if group.element not in self.compCpt:
					print("%s: Incorrectly started multi-part group" % (self.kanji.kId()))
				elif self.compCpt[group.element] != group.part - 1:
					print("%s: Incorrectly split multi-part group for %s - %d" % (self.kanji.kId(),group.element,group.part))
			self.compCpt[group.element] = group.part

	def handle_end_g(self):
		if self.group.parent is None:
			self.groups.append(self.group)
		self.group = self.group.parent

	def handle_start_path(self, attrs):
		if self.kanji is None or self.group is None:
			raise Exception("Stroke must be inside a kanji and group!")
		stroke = Stroke(self.group)
		if "kvg:type" in attrs:
			stroke.stype = unicode(attrs["kvg:type"])
		if "d" in attrs: stroke.svg = unicode(attrs["d"])
		self.group.childs.append(stroke)



class SVGHandler(BasicHandler):
	"""SVG handler for parsing final kanji files. It can handle single-kanji files or aggregation files. After parsing, the kanji are accessible through the kanjis member, indexed by their svg file name."""
	def __init__(self):
		BasicHandler.__init__(self)
		self.kanjis = {}
		self.currentKanji = None
		self.groups = []
		self.metComponents = set()

	def handle_start_g(self, attrs):
		group = StrokeGr()

		# Special case for handling the root
		if len(self.groups) == 0:
			idType, idVariantStr = str(attrs["id"]).split("_")
			idVariant = idVariantStr.split('-')
			if idType == "kvg:StrokePaths":
				pass
			elif idType == "kvg:StrokeNumbers":
				return
			else:
				raise Exception("Invalid root group id type (%s)" % (str(attrs["id"]),))
			self.currentKanji = Kanji(*idVariant)
			self.kanjis[self.currentKanji.code] = self.currentKanji
			self.compCpt = {}
		else:
			group.setParent(self.groups[-1])
	
		# Now parse group attributes
		if "kvg:element" in attrs: group.element = unicode(attrs["kvg:element"])
		if "kvg:variant" in attrs: group.variant = str(attrs["kvg:variant"])
		if "kvg:partial" in attrs: group.partial = str(attrs["kvg:partial"])
		if "kvg:original" in attrs: group.original = unicode(attrs["kvg:original"])
		if "kvg:part" in attrs: group.part = int(attrs["kvg:part"])
		if "kvg:number" in attrs: group.number = int(attrs["kvg:number"])
		if "kvg:tradForm" in attrs and str(attrs["kvg:tradForm"]) == "true": group.tradForm = True
		if "kvg:radicalForm" in attrs and str(attrs["kvg:radicalForm"]) == "true": group.radicalForm = True
		if "kvg:position" in attrs: group.position = unicode(attrs["kvg:position"])
		if "kvg:radical" in attrs: group.radical = unicode(attrs["kvg:radical"])
		if "kvg:phon" in attrs: group.phon = unicode(attrs["kvg:phon"])

		self.groups.append(group)

		if group.element: self.metComponents.add(group.element)
		if group.original: self.metComponents.add(group.original)

		# This code seems to be duplicated in the XML and SVG code and
		# possibly should be unified.
		if group.number:
			if not group.part:
				print("%s: Number specified, but part missing" % (self.currentKanji.kId()))
			ged = group.element + "n" + str(group.number)
			if group.part > 1:
				if (ged) not in self.compCpt:
					print("%s: Missing numbered group" % (self.currentKanji.kId()))
				elif self.compCpt[ged] != group.part - 1:
					print("%s: Incorrectly numbered group" % (self.currentKanji.kId()))
			# The group must not exist
			else:
				if (ged) not in self.compCpt:
					print("%s: Duplicate numbered group %d" % (self.currentKanji.kId(), group.number))
			self.compCpt[ged] = group.part
		# No number, just a part - groups restart with part 1, otherwise must
		# increase correctly
		elif group.part:
				# The group must exist already
			if group.part > 1:
				if (group.element) not in self.compCpt:
					print("%s: Incorrectly started multi-part group" % (self.currentKanji.kId()))
				elif self.compCpt[group.element] != group.part - 1:
					print("%s: Incorrectly splitted multi-part group" % (self.currentKanji.kId()))
			self.compCpt[group.element] = group.part

	def handle_end_g(self):
		if len(self.groups) == 0:
			return
		group = self.groups.pop()
		# End of kanji?
		if len(self.groups) == 1: # index 1 - ignore root group
			self.currentKanji.strokes = group
			self.currentKanji = None
			self.groups = []


	def handle_start_path(self, attrs):
		if len(self.groups) == 0: parent = None
		else: parent = self.groups[-1]
		stroke = Stroke(parent)
		if "kvg:type" in attrs:
			stroke.stype = unicode(attrs["kvg:type"])
		if "d" in attrs:
			stroke.svg = unicode(attrs["d"])
		self.groups[-1].childs.append(stroke)
