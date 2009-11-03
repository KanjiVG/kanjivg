#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, codecs, xml.sax, datetime
from kanjivg import *

def createSVG(out, kanji):
	out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	out.write("<!-- ")
	out.write(licenseString)
	out.write("\nThis file has been generated on %s, using the latest KanjiVG data to this date." % (datetime.date.today()))
	out.write("\n-->\n\n")
	out.write("""<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [
<!ATTLIST g
xmlns:kanjivg CDATA #FIXED "http://kanjivg.tagaini.net"
kanjivg:element CDATA #IMPLIED
kanjivg:variant CDATA #IMPLIED
kanjivg:partial CDATA #IMPLIED
kanjivg:original CDATA #IMPLIED
kanjivg:part CDATA #IMPLIED
kanjivg:tradForm CDATA #IMPLIED
kanjivg:radicalForm CDATA #IMPLIED
kanjivg:position CDATA #IMPLIED
kanjivg:radical CDATA #IMPLIED
kanjivg:phon CDATA #IMPLIED >
<!ATTLIST path
xmlns:kanjivg CDATA #FIXED "http://kanjivg.tagaini.net"
kanjivg:type CDATA #IMPLIED >
]>
<svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109" style="fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;">
<defs>
    <marker id="Triangle"
      viewBox="0 0 10 10" refX="0" refY="5" 
      markerUnits="strokeWidth"
      markerWidth="4" markerHeight="3"
      orient="auto" stroke="none" fill="#ff0000">
      <path d="M 0 0 L 10 5 L 0 10 z" />
    </marker>
</defs>
""")
	kanji.toSVG(out)
	out.write("</svg>\n")

if __name__ == "__main__":
	handler = KanjisHandler()
	xml.sax.parse("kanjivg.xml", handler)
	kanjis = handler.kanjis.values()

	for kanji in kanjis:
		out = codecs.open("generated/SVG/" + str(kanji.id) + ".svg", "w", "utf-8")
		createSVG(out, kanji)

