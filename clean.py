#!/usr/bin/env python

# This script removes unnecessary files such as backups from Emacs or
# old release files.

import os, glob

# Print debugging information if set to a true value.

verbose = True

# These files are generated by updatepublic.sh but are not part of the
# repository.

badFiles = glob.glob('kanjivg*.xml*')
badFiles.extend(glob.glob('kanjivg*.zip'))
for file in badFiles:
	if os.path.exists(file):
		if verbose:
			print("Removing %s" % (file) )
		os.remove(file)

# Emacs and possibly other editors create files with a ~ at the end
# for backup purposes.

emacsBackups = glob.glob('kanji/*~')
emacsBackups.extend(glob.glob('*~'))
emacsBackups.extend(glob.glob('.git/*~'))
for file in emacsBackups:
	if verbose:
		print("Removing %s" % (file) )
	os.remove(file)
