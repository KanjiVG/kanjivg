#!/usr/bin/env python

# This script removes unnecessary files such as backups from Emacs or
# old release files.

import os, glob

badFiles = glob.glob('kanjivg.xml')
for file in badFiles:
	if os.path.exists(file):
		os.remove(file)
emacsBackups = glob.glob('kanji/*~')
emacsBackups.extend(glob.glob('*~'))
for file in emacsBackups:
	os.remove(file)
