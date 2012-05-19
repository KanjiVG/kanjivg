#/bin/env python
# -*- mode: Python ; coding: utf-8 -*-
# Copyright  © 2012 Roland Sieker ( ospalh@gmail.com )
# Based on work by Alexandre Courbot, Copyright (C) 2011
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


'''Write the information in the kanjivg SVG files to a single xml
file, including variants and the stroke numbers.
'''

import xml.etree.ElementTree as ET


# Sample licence header
licenseString = """Copyright (C) 2009/2010/2011 Ulrich Apel.
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


svgNs = "http://www.w3.org/2000/svg"
kvgNs = "http://kanjivg.tagaini.net"



def addKanjiToTree(kanjiFn, tree):
    '''For each kanji where we have an SVG file, add a general element
to the XML tree and call addKanjiVariant fore each svg file, at least
oncce, more times when there are non-standard variants.'''
    
    pass

def addKanjiVariantToKanjiElement(kanjiElement, kanjiFn):
    '''Add the svg element of the kanjiVariant, wraped in an
identifying element, to the kanjiElement. This is the function that
actually reads the svg files.'''
    pass

def kanjiVgXmlTree(indir=u'kanji'):
    '''Create the outer structure of the Xml ElementTree, than add all
the data through addKanjiToTree. Return that tree.'''
    
    # Stuff to set up general inforamtion
    ET.register_namespace('svg', svgNs)
    ET.register_namespace('kvg', kvgNs)
    kanjiTree = ET.ElementTree()

    for kanjiFName in os.listdir(indir):
        # Only add a kanji entry when we have a ‘standard’ variant.
        if 9 == len(kanjiFName) and kanjiFName.endswith('.svg'):
            addKanjiToTree(kanjiFName, kanjiTree)

def writeKanjiData(indir=u'kanji', outFile='kanji_data.xml'):
    kanjiXmlTree = kanjiVgXmlTree(indir)
    ET.writeXml(kanjiXmlTree, outFile)



if __name__ == '__main__':
    # No command line options at the moment. If you want to other
    # input or output, call writeKajiData yourself, from another
    # script or the python console.
    writeKanjiData()
