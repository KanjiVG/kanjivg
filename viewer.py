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

	return StructuredKanji(kanji)

class MainWindow(QtGui.QWidget):
	def __init__(self, kanji, parent=None):
		QtGui.QWidget.__init__(self, parent)

		self.setWindowTitle('KanjiVG viewer')

		self.canvas = QtGui.QWidget(self)
		self.structure = QtGui.QTreeWidget(self)
		self.structure.setColumnCount(2)
		self.structure.setHeaderLabels([ 'Element', 'Original' ])

		hLayout = QtGui.QHBoxLayout()
		hLayout.addWidget(self.canvas)
		hLayout.addWidget(self.structure)

		self.setLayout(hLayout)

		self.buildStructureTree(None, kanji.components[0])

	def buildStructureTree(self, parent, group):
		for child in group.childs:
			original = ''
			if child.original != None:
				original = child.original
			item = QtGui.QTreeWidgetItem([ child.element, original ])
			if parent: parent.addChild(item)
			else: self.structure.addTopLevelItem(item)
			self.buildStructureTree(item, child)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit(0)

	kanji = loadKanji(sys.argv[1])

	app = QtGui.QApplication(sys.argv)
	mw = MainWindow(kanji)
	mw.resize(500, 400)

	mw.show()
	sys.exit(app.exec_())
