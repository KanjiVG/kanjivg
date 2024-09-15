#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2008  Alexandre Courbot
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

import xml.sax.handler

class BasicHandler(xml.sax.handler.ContentHandler):
	def __init__(self):
		xml.sax.handler.ContentHandler.__init__(self)
		self.elementsTree = []
	
	def currentElement(self):
		return str(self.elementsTree[-1])
		
	def startElement(self, qName, atts):
		self.elementsTree.append(str(qName))
		attrName = "handle_start_" + str(qName)
		if hasattr(self, attrName):
			rfunc = getattr(self, attrName)
			rfunc(atts)
		self.characters = ""
		return True
	
	def endElement(self, qName):
		attrName = "handle_data_" + qName
		if hasattr(self, attrName):
			rfunc = getattr(self, attrName)
			rfunc(self.characters)
		attrName = "handle_end_" + str(qName)
		if hasattr(self, attrName):
			rfunc = getattr(self, attrName)
			rfunc()
		self.elementsTree.pop()
		return True
	
	def characters(self, string):
		self.characters += string
		return True
