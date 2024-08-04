#!/usr/bin/env python

# This makes the file kvg-index.json which is used by the online
# KanjiVG viewer at https://kanjivg.tagaini.net/viewer.html. This
# script was contributed by
# https://github.com/KanjiVG/kanjivg/pull/430, but copy-pasted into
# the repository, see that pull request for details of why. This does
# not use the other kanjivg libraries in this directory.

if __name__ == "__main__":
	import glob
	import json
	import logging
	import os
	import re
	from collections import defaultdict
	from pathlib import Path

	def file_to_kanji(file):
		matched = re.match(r"^([0-9a-f]{5})(-.*)?\.svg$", file)
		if matched is None:
			return (None, None)

		return (chr(int(matched[1], 16)), matched[2])

	current_dir = Path(__file__).parent

	# The index we write to the file.
	index = defaultdict(list[str])

	files = sorted(
		map(os.path.basename, glob.glob(str(current_dir / "kanji" / "*.svg")))
	)
	for file in files:
		(kanji, _ex) = file_to_kanji(file)
		if kanji is None:
			logging.warning(f"Could not get kanji from {file}")
			continue

		index[kanji].append(file)

	with open(current_dir / "kvg-index.json", "w") as f:
		json.dump(
			index,
			f,
			ensure_ascii=False,
			indent="\t",
			separators=(",", ":"),
		)
		f.write("\n")
