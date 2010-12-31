#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2010  Alexandre Courbot
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

import sys, os, xml.sax, re, codecs, datetime
from PyQt4 import QtGui, QtCore
from kanjivg import *

def loadKanji(code):
	f = str(code)
	svgHandler = SVGHandler()
	parser = xml.sax.make_parser()
	parser.setContentHandler(svgHandler)
	parser.setFeature(xml.sax.handler.feature_external_ges, False)
	parser.setFeature(xml.sax.handler.feature_external_pes, False)
	parser.parse(os.path.join("data", f + ".svg"))

	kanji = svgHandler.kanjis.values()[0]
	return kanji

from PyQt4.QtCore import QPointF

def svg2Path(svg):
	'''Converts a SVG textual path into a QPainterPath'''
	retPath = QtGui.QPainterPath()

	# Add spaces between unseparated tokens
	t = svg
	t = re.sub(r"[a-zA-Z]\d|\d[a-zA-Z]", lambda(m): m.group(0)[0] + " " + m.group(0)[1], t)
	t = re.sub(r"[a-zA-Z]\d|\d[a-zA-Z]", lambda(m): m.group(0)[0] + " " + m.group(0)[1], t)
	t = re.sub(r"\-\d", lambda(m): " " + m.group(0), t)
	tokens = re.split("[ ,]+", t)

	# Convert to Qt path
	i = 0
	curAction = ''
	while i < len(tokens):
		if tokens[i] in ( "M", "m", "L", "l", "C", "c", "S", "s", "z", "Z" ):
			curAction = tokens[i]
			i += 1

		if curAction in ( "M", "m" ):
			dest = QPointF(float(tokens[i]), float(tokens[i + 1]))
			if curAction == "m": dest += retPath.currentPosition()
			retPath.moveTo(dest)
			i += 2
			lastControl = retPath.currentPosition()
		elif curAction in ( "L", "l" ):
			dest = QPointF(float(tokens[i]), float(tokens[i + 1]))
			if curAction == "l": dest += retPath.currentPosition()
			retPath.lineTo(dest)
			i += 2
			lastControl = retPath.currentPosition()
		elif curAction in ( "C", "c" ):
			p1 = QPointF(float(tokens[i]), float(tokens[i + 1]))
			p2 = QPointF(float(tokens[i + 2]), float(tokens[i + 3]))
			dest = QPointF(float(tokens[i + 4]), float(tokens[i + 5]))
			if curAction == "c":
				p1 += retPath.currentPosition()
				p2 += retPath.currentPosition()
				dest += retPath.currentPosition()
			retPath.cubicTo(p1, p2, dest)
			i += 6
			lastControl = p2
		elif curAction in ( "S", "s" ):
			p1 = retPath.currentPosition() * 2 - lastControl
			p2 = QPointF(float(tokens[i]), float(tokens[i + 1]))
			dest = QPointF(float(tokens[i + 2]), float(tokens[i + 3]))
			if curAction == "s":
				p2 += retPath.currentPosition()
				dest += retPath.currentPosition()
			retPath.cubicTo(p1, p2, dest)
			i += 4
			lastControl = p2
		elif curAction in ( "Z", "z" ):
			retPath.closeSubPath()
			lastControl = retPath.currentPosition()
		else:
			print "Unknown command %s while computing kanji path!" % ( tokens[i], )
			i += 1

	return retPath;

class SimpleStrokeRenderer:
	def __init__(self):
		self.strokesPen = QtGui.QPen()
		self.strokesPen.setWidth(2)
	
	def renderStroke(self, painter, stroke):
		painter.setPen(self.strokesPen)
		painter.drawPath(stroke.qPath)

class FancyStrokeRenderer:
	basicWeight = 1
	weightFactor = 1

	weights = {
		u'㇔' : (19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 7, 6, 6),
		u'㇔a' : (17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 8, 10, 12, 14),
		u'㇐' : (9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 15, 15, 14, 13, 12, 11, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 8),
		u'㇐a' : (11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 14, 14, 13, 12, 11, 10),
		u'㇐b' : (10, 10, 11, 11, 11, 12, 12, 12, 12, 13, 13, 14, 14, 13, 12, 11, 11, 11, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8),
		u'㇐c' : (9, 9, 9, 9, 9, 9, 10, 10,10, 10, 10, 10, 10, 11, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 15, 14, 13, 12, 11, 10, 9),
		u'㇑' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15, 14, 14, 13, 13, 12, 12, 11, 11, 11, 11, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9),
		u'㇑a' : (9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 13, 13, 13, 12, 12, 12, 12),
		u'㇒' : (8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 12, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26),
		u'㇏' : (19, 19, 18, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1),
		u'㇏a' : (20, 20, 20, 20, 20, 19, 19, 19, 19, 19, 18, 18, 18, 18, 17, 17, 16, 16, 15, 14, 14, 13, 12, 12, 11, 10, 10, 9, 8, 7, 6, 5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1),
		u'㇀' : (8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 12, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26),
		u'㇖' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 10, 11, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18),
		u'㇖a' : (10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 16, 15, 15, 14, 13, 12, 11, 10, 9, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19),
		u'㇖b' : (12, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 15, 14, 14, 13, 12, 11, 10, 9, 8, 7, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20),
		u'㇚' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15, 14, 14, 13, 13, 12, 12, 11, 11, 11, 11, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20),
		u'㇚a' : (18, 18, 17, 17, 16, 16, 15, 15, 14, 14, 13, 12, 11, 10, 9, 8, 8, 9, 9, 10, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20),
		u'㇚b' : (17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 8, 10, 12, 14),
		u'㇂' : (9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 13, 14, 14, 15, 15, 16, 16, 15, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 4, 5, 7, 9, 13, 15, 17, 19, 21, 23),
		u'㇙' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 12, 12, 13, 14, 14, 15, 15, 14, 14, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 9, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 12, 13, 13, 14, 15, 15, 16, 17, 17, 18, 19, 19, 20, 20),
		u'㇕' : (9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 15, 14, 14, 13, 13, 13, 12, 12, 12, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 10, 11, 12, 13, 13, 14, 14, 15, 15, 16, 15, 14, 13, 12, 11, 11, 11, 11, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9),
		u'㇕a' : (10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 14, 13, 13, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 8, 8, 9, 10, 11, 12, 13, 13, 14, 14, 15, 15, 16, 15, 14, 13, 12, 11, 11, 11, 11, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9),
		u'㇕b' : (10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 14, 13, 13, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 8, 8, 9, 10, 11, 12, 13, 13, 14, 14, 15, 15, 14, 14, 13, 12, 11, 10),
		u'㇕c' : (9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 15, 14, 14, 13, 13, 13, 12, 12, 12, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 10, 11, 12, 13, 13, 14, 14, 15, 15, 14, 13, 12, 11, 10, 10),
		u'㇗' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 12, 12, 12, 11, 11, 11, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 8, 8, 8, 8, 8, 8),
		u'㇗a' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 12, 12, 12, 11, 11, 11),
		u'㇛' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 9, 9, 9, 10, 11, 12, 13, 14, 15, 14, 14, 13, 12, 11, 10, 9, 8, 7, 6, 6, 5, 5, 4, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7),
		u'㇜' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 10, 11, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18),
		u'㇇' : (8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 10, 10, 9, 9, 8, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26),
		u'㇇a' : (10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 16, 15, 15, 14, 13, 12, 11, 10, 9, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19),
		u'㇄' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15, 14, 14, 13, 13, 12, 12, 12, 11, 11, 11, 11, 11, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 13, 13, 13, 12, 12, 12, 11, 11, 10, 10, 10, 10, 10, 9, 9, 9, 9, 8, 8),
		u'㇄a' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15, 14, 14, 13, 13, 12, 12, 12, 11, 11, 11, 11, 11, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 11, 11, 12, 12, 13, 13, 14, 13, 12, 11, 10),
		u'㇆' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21),
		u'㇆a' : (10, 10, 11, 11, 12, 13, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21),
		u'㇆b' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 9, 10, 10, 11, 11, 12, 12, 12, 11, 11, 11, 10, 10, 9, 9, 8, 8, 9, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22),
		u'㇟' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15, 14, 14, 14, 13, 13, 13, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 10, 9, 8, 7, 6, 5, 4, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23),
		u'㇟a' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15, 14, 14, 14, 13, 13, 13, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9),
		u'㇟b' : (19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 2, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23),
		u'㇊' : (),
		u'㇉' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15, 14, 14, 13, 13, 12, 12, 12, 11, 11, 11, 11, 11, 10, 9, 10, 9, 9, 9, 9, 9, 9, 9, 10, 11, 12, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 9, 9, 9, 10, 10, 11, 11, 12, 12, 14, 14, 13, 13, 12, 12, 11, 13, 11, 10, 10, 9, 9, 9, 10, 11, 12, 13, 14, 15, 16, 17, 17, 18, 18, 19, 19),
		u'㇋' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 10, 10, 10, 10, 10, 9, 9, 8, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 13, 12, 11, 11, 10, 10, 9, 9, 8, 8, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18),
		u'㇌' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 10, 10, 10, 10, 10, 9, 9, 8, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 13, 12, 11, 11, 10, 10, 10, 11, 11, 12, 12, 13, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 21),
		u'㇈' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 10, 10, 11, 11, 12, 12, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 11, 11, 11, 10, 9, 8, 7, 6, 5, 4, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23),
		u'㇈a' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 11, 12, 13, 13, 14, 14, 15, 15, 16, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 5, 7, 9, 13, 15, 17, 19, 21, 23),
		u'㇈b' : (9, 9, 10, 11, 11, 12, 13, 13, 14, 15, 15, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 9, 9, 10, 10, 10, 11, 11, 12, 12, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 11, 11, 11, 10, 9, 8, 7, 6, 5, 4, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23),
		u'㇅' : (8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15, 14, 14, 13, 13, 12, 12, 12, 11, 11, 11, 11, 11, 10, 9, 10, 9, 9, 9, 9, 9, 9, 9, 10, 11, 12, 13, 14, 14, 15, 15, 16, 16, 16, 16, 15, 15, 14, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 9, 9, 9, 10, 10, 11, 11, 12, 12, 14, 14, 13, 13, 12, 12, 11, 13, 11, 10, 10),


	}

	def __init__(self):
		self.fallback = SimpleStrokeRenderer()
		self.strokesPen = QtGui.QPen()
		self.strokesPen.setWidth(2)
	
	def renderStroke(self, painter, stroke):
		if stroke.stype in self.weights: layout = self.weights[stroke.stype]
		elif stroke.stype[0] in self.weights: layout = self.weights[stroke.stype[0]]
		else:
			self.fallback.renderStroke(painter, stroke)
			return
			
		ppen = QtGui.QPen(self.strokesPen)
		ppen.setCapStyle(QtCore.Qt.RoundCap)
		segmentLength = stroke.qPath.length() / len(layout)
		startPoint = 0.0
		for i in range(len(layout)):
			ppen.setWidthF(self.basicWeight + (3.8 - 0.1 * layout[i]) * self.weightFactor)
			self.renderPartialStroke(painter, ppen, stroke.qPath, startPoint, segmentLength)
			startPoint += segmentLength

	def renderPartialStroke(self, painter, pen, stroke, startPoint, segmentLength):
		painter.save()
		ppen = QtGui.QPen(pen)
		dashes = [ 0.0, startPoint / ppen.widthF(), segmentLength / ppen.widthF(), stroke.length() / ppen.widthF() ]
		ppen.setDashPattern(dashes)
		painter.setPen(ppen)
		painter.drawPath(stroke)
		painter.restore()

class StrokesWidget(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		self.strokesRenderer = FancyStrokeRenderer()

		self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding);
	
		self.selectedStrokesPen = QtGui.QPen()
		self.selectedStrokesPen.setWidth(2)
		self.selectedStrokesPen.setColor(QtCore.Qt.red)

		self.boundingPen = QtGui.QPen()
		self.boundingPen.setStyle(QtCore.Qt.DotLine)

	def setKanji(self, kanji):
		self.kanji = kanji
		self.__loadGroup(self.kanji.root)

	def __loadGroup(self, group):
		rect = QtCore.QRectF()
		pwidth = 1.0
		for child in group.childs:
			if isinstance(child, StrokeGr):
				self.__loadGroup(child)
			else:
				child.qPath = svg2Path(child.svg)
				child.boundingRect = child.qPath.controlPointRect().adjusted(-pwidth, -pwidth, pwidth, pwidth)
			rect |= child.boundingRect
		group.boundingRect = rect

	def paintEvent(self, event):
		if not self.kanji: return
		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		size = self.size()
		painter.scale(size.width() / 109.0, size.height() / 109.0)

		drawLater = []
		self.__renderGroup(self.kanji.root, painter, drawLater)

		painter.setPen(self.selectedStrokesPen)
		for child in drawLater:
			painter.drawPath(child.qPath)
			# Also draw a tip to indicate the direction
			lastPoint = child.qPath.pointAtPercent(1)
			lastAngle = child.qPath.angleAtPercent(0.95)
			line = QtCore.QLineF(0, 0, 4, 4)
			line.translate(lastPoint)
			line.setAngle(lastAngle + 150)
			painter.drawLine(line)
			line.setAngle(lastAngle - 150)
			painter.drawLine(line)
			

	def __renderGroup(self, group, painter, drawLater):
		for child in group.childs:
			if isinstance(child, StrokeGr):
				self.__renderGroup(child, painter, drawLater)
				if child in self.selection:
					painter.setPen(self.boundingPen)
					painter.drawRect(child.boundingRect)
			else:
				if child in self.selection: drawLater.append(child)
				else:
					self.strokesRenderer.renderStroke(painter, child)

class KanjiStructModel(QtCore.QAbstractItemModel):
	columns = [ 'Element', 'Original', 'Position', 'Phon', 'Part' ]
	StrokeRole = QtCore.Qt.UserRole

	def __init__(self, kanji = None, parent = None):
		QtCore.QAbstractItemModel.__init__(self, parent)
		self.setKanji(kanji)

	def setKanji(self, kanji):
		self.kanji = kanji

	def index(self, row, column, parent):
		if not self.kanji: return QtCore.QModelIndex()

		if not parent.isValid(): return self.createIndex(row, column, kanji.root)
		group = parent.internalPointer().childs[parent.row()]
		if not isinstance(group, StrokeGr) or row >= len(group.childs) or column >= len(KanjiStructModel.columns):
			return QtCore.QModelIndex()
		return self.createIndex(row, column, group)

	def data(self, index, role):
		if not self.kanji or not index.isValid(): return QtCore.QVariant()

		item = index.internalPointer().childs[index.row()]
		if role == KanjiStructModel.StrokeRole:
			return item
		column = index.column()
		if isinstance(item, StrokeGr) and role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
			if column == 0: return item.element
			elif column == 1: return item.original
			elif column == 2: return item.position
			elif column == 3: return item.phon
			elif column == 4: return item.part
		elif isinstance(item, Stroke) and role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
			if column == 0: return item.stype
		return QtCore.QVariant()

	def setData(self, index, value, role):
		if not self.kanji or not index.isValid(): return QtCore.QVariant()
		item = index.internalPointer().childs[index.row()]
		column = index.column()
		if isinstance(item, StrokeGr) and role == QtCore.Qt.EditRole:
			if column == 0: item.element = value
			elif column == 1: item.original = value
			elif column == 2: item.position = value
			elif column == 3: item.phon = value
			elif column == 4: item.part = value
			else: return False
			return True
		elif isinstance(item, Stroke) and role == QtCore.Qt.EditRole:
			if column == 0: item.type = value
			else: return False
			return True
		return False

	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole and section < len(KanjiStructModel.columns):
			return KanjiStructModel.columns[section]
		else: return QtCore.QVariant()

	def flags(self, index):
		if not index.isValid(): return 0
		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

	def parent(self, index):
		if not self.kanji or not index.isValid(): return QtCore.QModelIndex()
		p = index.internalPointer()
		if p == self.kanji.root: return QtCore.QModelIndex()
		else: return self.createIndex(p.parent.childs.index(p), 0, p.parent)

	def rowCount(self, parent):
		if not self.kanji: return 0
		if not parent.isValid(): return len(kanji.root.childs)
		group = parent.internalPointer().childs[parent.row()]
		if not isinstance(group, StrokeGr): return 0
		return len(group.childs)

	def columnCount(self, parent):
		return len(KanjiStructModel.columns)

class KanjiStructDelegate(QtGui.QStyledItemDelegate):
	positions = [ "", "top", "bottom", "left", "right", "tare" ]
	def __init__(self, parent=None):
		QtGui.QStyledItemDelegate.__init__(self, parent)

	def createEditor(self, parent, option, index):
		item = index.internalPointer().childs[index.row()]
		if isinstance(item, StrokeGr):
			if index.column() in (0, 1, 3):
				ret = QtGui.QStyledItemDelegate.createEditor(self, parent, option, index)
			elif index.column() == 2:
				ret = QtGui.QComboBox(parent)
				ret.addItems(KanjiStructDelegate.positions)
			elif index.column() == 4:
				ret = QtGui.QSpinBox(parent)
				ret.setSpecialValueText("None")
				ret.setMinimum(0)
				ret.setMaximum(10)
		elif isinstance(item, Stroke):
			ret = QtGui.QStyledItemDelegate.createEditor(self, parent, option, index)
		return ret

	def setEditorData(self, editor, index):
		item = index.internalPointer().childs[index.row()]
		if isinstance(item, StrokeGr):
			if index.column() in (0, 1, 3):
				QtGui.QStyledItemDelegate.setEditorData(self, editor, index)
			elif index.column() == 2:
				pos = index.model().data(index, QtCore.Qt.EditRole)
				if pos in KanjiStructDelegate.positions:
					editor.setCurrentIndex(KanjiStructDelegate.positions.index(pos))
			elif index.column() == 4:
				val = index.model().data(index, QtCore.Qt.EditRole)
				editor.setValue(val)
		elif isinstance(item, Stroke):
			QtGui.QStyledItemDelegate.setEditorData(self, editor, index)

	def setModelData(self, editor, model, index):
		if index.column() in (0, 1, 3):
			QtGui.QStyledItemDelegate.setModelData(self, editor, model, index)
		elif index.column() == 2:
			model.setData(index, editor.currentText(), QtCore.Qt.EditRole)
		elif index.column() == 4:
			val = editor.value()
			if val == 0: val = None
			model.setData(index, val, QtCore.Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)


class KanjiStructView(QtGui.QTreeView):
	__pyqtSignals__ = ("selectionChanged()")

	def __init__(self, parent=None):
		QtGui.QTreeView.__init__(self, parent)

	def selectionChanged(self, selected, deselected):
		QtGui.QTreeView.selectionChanged(self, selected, deselected)
		self.emit(QtCore.SIGNAL("selectionChanged()"))

class MainWindow(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)

		self.setWindowTitle('KanjiVG viewer')

		self.canvas = StrokesWidget(self)
		self.canvas.selection = []

		self.kanjiModel = KanjiStructModel(self)
		self.structure = KanjiStructView(self)
		self.structure.setItemDelegate(KanjiStructDelegate())
		self.structure.setModel(self.kanjiModel)

		hLayout = QtGui.QHBoxLayout()
		hLayout.addWidget(self.canvas)
		hLayout.addWidget(self.structure)

		self.setLayout(hLayout)

		self.connect(self.structure, QtCore.SIGNAL('selectionChanged()'), self.onSelectionChanged)

	def setKanji(self, kanji):
		self.canvas.setKanji(kanji)
		self.kanjiModel.setKanji(kanji)

	def onSelectionChanged(self):
		self.canvas.selection = []
		for index in self.structure.selectedIndexes():
			self.canvas.selection.append(index.model().data(index, KanjiStructModel.StrokeRole))
		self.canvas.update()


from createsvgfiles import createSVG

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit(0)

	kanji = loadKanji(sys.argv[1])

	app = QtGui.QApplication(sys.argv)
	mw = MainWindow()
	mw.resize(500, 400)
	mw.setKanji(kanji)

	mw.show()
	ret = app.exec_()
	createSVG(codecs.open('out.svg', 'w', 'utf-8'), kanji)
	sys.exit(ret)
