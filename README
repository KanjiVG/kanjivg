This is the KanjiVG source repository. It is rather raw, so you probably want
to process it before using it.

Licence
-------
KanjiVG is copyright Ulrich Apel and released under the Creative Commons
Attribution-Share Aline 3.0 licence:

http://creativecommons.org/licenses/by-sa/3.0/

See the COPYING file for more details.

Description
-----------
This repository is made of two directories: SVG and XML, as well as a set of
Python scripts.

The SVG and XML directories contain the structural and graphical description
of each kanji, respectively. Each Kanji is described by a file in both
directories, named after its unicode encoding in hexadecimal. Variations of
a Kanji are followed by a textual suffix.

The XML file describes the different components and strokes that make the 
kanji in a structured way. In addition, other information such as radicals
and phonetic keys are also given as attributes.

The SVG file guidelines for the graphical representation of various properties
of the Kanji. It is visible as is, but is more interesting when its various
layers are taken differently. Layers are accessible through an attribute:

- The StrokesPaths layer contains <path> elements that should be drawn in
order to render the Kanji. The <path> elements are given following the
correct stroke order and match their corresponding <stroke> element in the XML
description.
- The StrokesNumbers layer contains <text> elements that give a hint as to
where the number of a given stroke should appear for maximum visibility.

There are other layers but they are mostly here as helpers to allow easy
editing within your favorite SVG editor.

The official KanjiVG release is a single XML file that merges the information
contained within the two sets of files. Its syntax is close and compatible with
the individual XML files, but stroke paths and stroke number hints are merged
with every path.

The Python scripts are here to maintain the data and perform simple processing.
- The xmlhandler.py and kanjivg.py files contain a loader for the KanjiVG 
release file and different in-memory representations.

- harmonize-svg.py is used to ensure all SVG files have the same structure and
same attributes despite of the editor that has been used to alter them. SVG
editors tend to mess a lot with the styles and the structure of the file they
manipulate and add plenty of attributes. This script loads the essential
information from altered SVG files and regenerate a clean file from the
template.svg file. All changed SVG files must be passed through this filter
before being commited.


