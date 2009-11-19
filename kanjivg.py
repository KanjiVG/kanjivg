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

from xmlhandler import *

# Sample licence header
licenseString = """Copyright (C) 2009 Ulrich Apel.
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
	"""Describes a kanji. The root stroke group is accessible from the root member."""
	def __init__(self, id):
		self.id = id
		self.midashi = None
		self.root = None

	def toSVG(self, out, indent = 0):
		self.root.toSVG(out, self.id, [0])

	def toXML(self, out, indent = 0):
		out.write("\t" * indent + '<kanji midashi="%s" id="%s">\n' % (self.midashi, self.id))
		self.root.toXML(out, 0)
		out.write("\t" * indent + '</kanji>\n')

	def simplify(self):
		self.root.simplify()

	def getStrokes(self):
		return self.root.getStrokes()
		

class StrokeGr:
	"""Describes a stroke group belonging to a kanji as closely as possible to the XML format. Sub-stroke groups or strokes are available in the childs member. They can either be of class StrokeGr or Stroke so their type should be checked."""
	def __init__(self, parent):
		self.parent = parent
		if parent: parent.childs.append(self)
		# Element of strokegr, or midashi for kanji
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

	def toSVG(self, out, idRoot, idCpt = [0], indent = 0):
		if idCpt[0] == 0:
			gid = "strokes-" + idRoot
		else:
			if (self.element): elt = self.element
			else: elt = self.original
			gid = "c" + idRoot
			if elt: gid += "-" + hex(ord(elt))[2:]
			else: gid += "-xxxx"
			gid += "-" + str(idCpt[0])
		idCpt[0] += 1
		idString = ' id="%s"' % (gid)
		eltString = ""
		if self.element: eltString = ' kanjivg:element="%s"' % (self.element)
		variantString = ""
		if self.variant: variantString = ' kanjivg:variant="true"'
		partialString = ""
		if self.partial: partialString = ' kanjivg:partial="true"'
		origString = ""
		if self.original: origString = ' kanjivg:original="%s"' % (self.original)
		partString = ""
		if self.part: partString = ' kanjivg:part="%d"' % (self.part)
		numberString = ""
		if self.number: numberString = ' kanjivg:number="%d"' % (self.number)
		tradFormString = ""
		if self.tradForm: tradFormString = ' kanjivg:tradForm="true"'
		radicalFormString = ""
		if self.radicalForm: radicalFormString = ' kanjivg:radicalForm="true"'
		posString = ""
		if self.position: posString = ' kanjivg:position="%s"' % (self.position)
		radString = ""
		if self.radical: radString = ' kanjivg:radical="%s"' % (self.radical)
		phonString = ""
		if self.phon: phonString = ' kanjivg:phon="%s"' % (self.phon)
		out.write("\t" * indent + '<g%s%s%s%s%s%s%s%s%s%s%s%s>\n' % (idString, eltString, partString, numberString, variantString, origString, partialString, tradFormString, radicalFormString, posString, radString, phonString))

		for child in self.childs:
			child.toSVG(out, idRoot, idCpt, indent + 1)

		out.write("\t" * indent + '</g>\n')

	def toXML(self, out, indent = 0):
		eltString = ""
		if self.element: eltString = ' element="%s"' % (self.element)
		variantString = ""
		if self.variant: variantString = ' variant="true"'
		partialString = ""
		if self.partial: partialString = ' partial="true"'
		origString = ""
		if self.original: origString = ' original="%s"' % (self.original)
		partString = ""
		if self.part: partString = ' part="%d"' % (self.part)
		numberString = ""
		if self.number: numberString = ' number="%d"' % (self.number)
		tradFormString = ""
		if self.tradForm: tradFormString = ' tradForm="true"'
		radicalFormString = ""
		if self.radicalForm: radicalFormString = ' radicalForm="true"'
		posString = ""
		if self.position: posString = ' position="%s"' % (self.position)
		radString = ""
		if self.radical: radString = ' radical="%s"' % (self.radical)
		phonString = ""
		if self.phon: phonString = ' phon="%s"' % (self.phon)
		out.write("\t" * indent + '<strokegr%s%s%s%s%s%s%s%s%s%s%s>\n' % (eltString, partString, numberString, variantString, origString, partialString, tradFormString, radicalFormString, posString, radString, phonString))

		for child in self.childs: child.toXML(out, indent + 1)

		out.write("\t" * indent + '</strokegr>\n')

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
	def __init__(self):
		self.stype = None
		self.svg = None

	def toSVG(self, out, idRoot, idCpt, indent = 0):
		pid = "s" + idRoot + "-" + str(idCpt[0])
		idCpt[0] += 1
		if not self.svg: out.write("\t" * indent + '<path id="%s" d="" kanjivg:type="%s"/>\n' % (pid, self.stype))
		else: out.write("\t" * indent + '<path id="%s" d="%s" kanjivg:type="%s"/>\n' % (pid, self.svg, self.stype))

	def toXML(self, out, indent = 0):
		if not self.svg: out.write("\t" * indent + '<stroke type="%s"/>\n' % (self.stype))
		else: out.write("\t" * indent + '<stroke type="%s" path="%s"/>\n' % (self.stype, self.svg))

class StructuredKanji:
	"""A more structured format for the kanji, where all the parts of groups are grouped together."""
	def __init__(self, kanji):
		self.components = []
		self.strokes = []

		stk = []
		self.__buildStructure(kanji.root, stk, None)

	def __mostCommonAncestor(self, np, npp):
		# Update the parent to the most common parent of all parts
		npSave = np
		if np != None:
			while np != npp:
				np = np.parent
				if np == None:
					npp = npp.parent
					np = npSave
		return np

	def __buildStructure(self, group, stk, parent):
		# Find the component if it exists already, or create it as needed
		# Number exists and part is > 1, we must find a component which number matches.
		newParent = None
		if group.number > 0 and group.part > 1:
			for component in self.components:
				if component.element == group.element and component.number == group.number:
					newParent = component
					component.parent = self.__mostCommonAncestor(component.parent, parent)
					break
			# Should never happen
			if not newParent: raise Exception("Unable to find component!")
		# No number but a part, we need the latest component which element matches
		elif group.part > 1:
			for component in self.components:
				if component.element == group.element:
					newParent = component
					component.parent = self.__mostCommonAncestor(component.parent, parent)
					break
			if not newParent: raise Exception("Unable to find component!")
		# Either a single part component or a first part - we need to create the component
		else: 
			# Only do that if the current group has an element
			if group.element:
				newParent = StructuredStrokeGroup(parent, group.element, group.original, group.number)
				self.components.append(newParent)
			# Else keep the same parent
			else: newParent = parent

		if newParent != parent: stk.append(newParent)

		# Add the found group as a child of its parent
		if parent: parent.childs.append(newParent)

		# Now parse the childs of the group
		for child in group.childs:
			# Another group - we need to call ourselves recursively to build it
			if isinstance(child, StrokeGr):
				self.__buildStructure(child, stk, newParent)
			# A stroke - just add it to our list as well as
			# to the list of all the parents on the stack
			elif isinstance(child, Stroke):
				self.strokes.append(child)
				for pGroup in stk: pGroup.strokes.append(child)
				# Set the direct parent of the child
				child.parent = newParent

		if newParent != parent: stk.pop()

class StructuredStrokeGroup:
	def __init__(self, parent, element, original, number):
		self.parent = parent
		self.element = element
		self.original = original
		self.number = number
		self.childs = []
		self.strokes = []

class KanjisHandler(BasicHandler):
	"""XML handler for parsing kanji files. It can handle single-kanji files or aggregation files. After parsing, the kanjis are accessible through the kanjis member, indexed by their svg file name."""
	def __init__(self):
		BasicHandler.__init__(self)
		self.kanjis = {}
		self.currentKanji = None
		self.groups = []

	def handle_start_kanji(self, attrs):
		id = str(attrs["id"])
		self.currentKanji = Kanji(id)
		self.currentKanji.midashi = unicode(attrs["midashi"])
		# Check that the ID matches the midashi
		midashiNumber = "%04x" % (realord(self.currentKanji.midashi))
		if midashiNumber != id[:len(midashiNumber)]:
			print "Warning: id does not match midashi (%s(%s) %s)" % (self.currentKanji.midashi, midashiNumber, id)
		self.kanjis[id] = self.currentKanji

		self.compCpt = {}

	def handle_end_kanji(self):
		if len(self.groups) != 0:
			print "WARNING: stroke groups remaining after reading kanji!"
		self.currentKanji = None
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

		if group.number:
			if not group.part: print "%s: Number specified, but part missing" % (self.currentKanji.id)
			# The group must exist already
			if group.part > 1:
				if not self.compCpt.has_key(group.element + str(group.number)):
					print "%s: Missing numbered group" % (self.currentKanji.id)
				elif self.compCpt[group.element + str(group.number)] != group.part - 1:
					print "%s: Incorrectly numbered group" % (self.currentKanji.id)
			# The group must not exist
			else:
				if self.compCpt.has_key(group.element + str(group.number)):
					print "%s: Duplicate numbered group" % (self.currentKanji.id)
			self.compCpt[group.element + str(group.number)] = group.part
		# No number, just a part - groups restart with part 1, otherwise must
		# increase correctly
		elif group.part:
				# The group must exist already
			if group.part > 1:
				if not self.compCpt.has_key(group.element):
					print "%s: Incorrectly started multi-part group" % (self.currentKanji.id)
				elif self.compCpt[group.element] != group.part - 1:
					print "%s: Incorrectly splitted multi-part group" % (self.currentKanji.id)
			self.compCpt[group.element] = group.part

	def handle_end_strokegr(self):
		group = self.groups.pop()
		if len(self.groups) == 0:
			if self.currentKanji.root:
				print "WARNING: overwriting root of kanji!"
			self.currentKanji.root = group

	def handle_start_stroke(self, attrs):
		stroke = Stroke()
		stroke.stype = unicode(attrs["type"])
		if attrs.has_key("path"): stroke.svg = unicode(attrs["path"])
		self.groups[-1].childs.append(stroke)
