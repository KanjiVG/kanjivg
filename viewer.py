import sys, os, xml.sax, re
from PyQt4 import QtGui, QtCore
from kanjivg import *


class KanjiStrokeHandler(BasicHandler):
	def __init__(self):
		BasicHandler.__init__(self)
		self.strokes = []
		self.active = False

	def handle_start_path(self, attrs):
		strokeData = attrs["d"]
		# Replace spaces between digits by the comma separator
		strokeData = re.sub('(\d) (\d)', '\\1,\\2', strokeData)
		strokeData = re.sub("[\n\t ]+", "", strokeData)

		self.strokes.append(strokeData)

	def handle_start_g(self, attrs):
		if attrs.has_key("id") and attrs["id"] == "Vektorbild": self.active = True

def loadKanji(code):
	f = str(code)
	descHandler = KanjisHandler()
	xml.sax.parse(os.path.join("XML", f + ".xml"), descHandler)

	parser = xml.sax.make_parser()
	svgHandler = KanjiStrokeHandler()
	parser.setContentHandler(svgHandler)
	parser.setFeature(xml.sax.handler.feature_external_ges, False)
	parser.setFeature(xml.sax.handler.feature_external_pes, False)
	svgFile = os.path.join("SVG", f + ".svg")
	if os.path.exists(svgFile):
		parser.parse(svgFile)

	kanji = descHandler.kanjis.values()[0]
	desc = kanji.getStrokes()
	svg = svgHandler.strokes
	if len(desc) != len(svg):
		print "Stroke count mismatch!"
		sys.exit(1)

	for stroke, path in zip(desc, svg):
		stroke.svg = path

	return kanji

from PyQt4.QtCore import QPointF

def svg2Path(svg):
	retPath = QtGui.QPainterPath()
	#retPath.setFillRule(QtGui.WindingFill)

	# Add spaces between unseparated tokens
	t = svg
	t = re.sub(r"[a-zA-Z]\d|\d[a-zA-Z]", lambda(m): m.group(0)[0] + " " + m.group(0)[1], t)
	t = re.sub(r"[a-zA-Z]\d|\d[a-zA-Z]", lambda(m): m.group(0)[0] + " " + m.group(0)[1], t)
	t = re.sub(r"\-\d", lambda(m): " " + m.group(0), t)
	tokens = re.split(" +|,", t)

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

	#while r.search(svg, pos):
		#pos = r.lastindex


class StrokesWidget(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding);

	def setKanji(self, kanji):
		self.kanji = kanji
		for stroke in self.kanji.getStrokes():
			stroke.qPath = svg2Path(stroke.svg)

	def paintEvent(self, event):
		if not self.kanji: return
		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		pen = QtGui.QPen(painter.pen())
		pen.setWidth(5)
		painter.setPen(pen)
		size = self.size()
		painter.scale(size.width() / 109.0, size.height() / 109.0)

		for stroke in self.kanji.getStrokes():
			painter.drawPath(stroke.qPath)

class MainWindow(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)

		self.setWindowTitle('KanjiVG viewer')

		self.canvas = StrokesWidget(self)
		self.structure = QtGui.QTreeWidget(self)
		self.structure.setColumnCount(2)
		self.structure.setHeaderLabels([ 'Element', 'Original' ])

		hLayout = QtGui.QHBoxLayout()
		hLayout.addWidget(self.canvas)
		hLayout.addWidget(self.structure)

		self.setLayout(hLayout)

	def setKanji(self, kanji):
		self.canvas.setKanji(kanji)
		self.__buildStructureTree(None, kanji.root)

	def __buildStructureTree(self, parent, group):
		for child in group.childs:
			if isinstance(child, StrokeGr):
				element = '<none>'
				original = ''
				if child.element != None: element = child.element
				if child.original != None: original = child.original
				item = QtGui.QTreeWidgetItem([ element, original ])
				if parent: parent.addChild(item)
				else: self.structure.addTopLevelItem(item)
				self.__buildStructureTree(item, child)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit(0)

	kanji = loadKanji(sys.argv[1])

	app = QtGui.QApplication(sys.argv)
	mw = MainWindow()
	mw.resize(500, 400)
	mw.setKanji(kanji)

	mw.show()
	sys.exit(app.exec_())
