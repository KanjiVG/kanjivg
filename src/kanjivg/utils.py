import sys, os, warnings

PYTHON_VERSION_MAJOR = sys.version_info[0]

if PYTHON_VERSION_MAJOR < 3:
	# In python 2, io.open does not support encoding parameter
	from codecs import open
else:
	from io import open
	# In python 3, strings are used so unicode() is a pass-through
	def unicode(s):
		return s

# Given a string "id", either turn it into its numerical Unicode
# value, or if it appears to be a hexadecimal string, convert that
# into a number, then convert the number into a five digit hexadecimal
# for use as a file name.

def canonicalId(id):
	if isinstance(id, str):
		idLen = len(id)
		if idLen == 1:
			id = ord(id)
		elif idLen >= 2 and idLen <= 5:
			id = int(id, 16)
		else:
			raise ValueError("Character id must be a 1-character string with the character itself, or 2-5 hex digit unicode codepoint.")
	if not isinstance(id, int):
		raise ValueError("canonicalId: id must be int or str")
	if id > 0xf and id <= 0xfffff:
		return "%05x" % (id)
	raise ValueError("Character id out of range")

class SvgFileInfo:
	def __init__(self, file, dir):
		self.path = os.path.join(dir, file)
		self.OK = True
		if file[-4:].lower() != ".svg":
			warnings.warn("File should have .svg extension. (%s)" % (str(self.path)))
			self.OK = False
			return
		parts = (file[:-4]).split('-')
		if len(parts) == 2:
			self.variant = parts[1]
		elif len(parts) != 1:
			warnings.warn("File should have at most 2 parts separated by a dash. (%s)" % (str(file)))
			self.OK = False
			return
		self.id = parts[0]
		if self.id != canonicalId(self.id):
			warnings.warn("File name not in canonical format (%s)" % (str(self.path)))
			self.OK = False
			return


	def __repr__(self):
		 return repr(vars(self))

	def read(self, SVGHandler=None):	
		if SVGHandler is None:
			from kanjivg import SVGHandler 
		handler = SVGHandler()
		parseXmlFile(self.path, handler)
		parsed = list(handler.kanjis.values())
		if len(parsed) != 1:
			raise Exception("File does not contain 1 kanji entry. (%s)" % (self.path))
		return parsed[0]

# Parse kanjivg.xml

def parseXmlFile(path, handler):
	from xml.sax import parse
	parse(path, handler)

# Make a list of the SVG files in kanji

def listSvgFiles(dir):
	list = []
	for f in os.listdir(dir):
		sfi = SvgFileInfo(f, dir)
		if sfi.OK:
			list.append(sfi)
	return list

# Read in the file kanjivg.xml

def readXmlFile(path, KanjisHandler=None):
	if KanjisHandler is None:
		from kanjivg import KanjisHandler
	handler = KanjisHandler()
	parseXmlFile(path, handler)
	parsed = list(handler.kanjis.values())
	if len(parsed) == 0:
		raise Exception("File does not contain any kanji entries. (%s)" % (path))
	return handler.kanjis

