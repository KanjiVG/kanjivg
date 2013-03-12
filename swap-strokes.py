#! /usr/bin/env python3
# -*- coding: utf-8 ; mode: python -*-
# © Copyright 2013 ospalh@gmail.com
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import argparse
import re

"""
Swap stroke data in KanjiVG files.

This is a helper script to fix problems where strokes or stroke
numbers are out of order. Run as script with --help for more info.

N.B.:
This is rather brittle. It does not use any kind of xml parser, but
looks for strings commonly found in the svg files. Use this only as a
support tool. Check that the script did what you expected after
running it.
"""

__version__ = '0.1.0'

number_text_pattern = '>{0}</text>'
stroke_re = '^\s.*-s{0}" kvg:type=".*" d="(.*)"/>'
stroke_text_pattern = '-s{0}" kvg:type="'


def swap_numbers(kanji, a, b):
    """Swap stroke numbers in a kanjivg file"""
    # We do hardly any checking. If something is wrong, just blow up.
    with open(kanji) as kf:
        lines = kf.readlines()
    num_a = -1
    num_b = -1
    line_a = ''
    line_b = ''
    line_a_pattern = number_text_pattern.format(a)
    line_b_pattern = number_text_pattern.format(b)
    for n, l in enumerate(lines):
        if line_a_pattern in l:
            num_a = n
            line_a = l
        if line_b_pattern in l:
            num_b = n
            line_b = l
    if num_a < 0 or num_b < 0:
        raise RuntimeError("Did not find both lines")
    lines[num_a] = line_b.replace(line_b_pattern, line_a_pattern)
    lines[num_b] = line_a.replace(line_a_pattern, line_b_pattern)
    with open(kanji, 'w') as kf:
        for l in lines:
            kf.write(l)


def swap_stroke_data(kanji, a, b):
    """Swap the stroke data in a kanjivg file"""
    # We do hardly any checking. If something is wrong, just blow up.
    with open(kanji) as kf:
        lines = kf.readlines()
    num_a = -1
    num_b = -1
    line_a_match = None
    line_b_match = None
    line_a_re = stroke_re.format(a)
    line_b_re = stroke_re.format(b)
    for n, l in enumerate(lines):
        m = re.search(line_a_re, l)
        if m:
            num_a = n
            line_a_match = m
        m = re.search(line_b_re, l)
        if m:
            num_b = n
            line_b_match = m
    if num_a < 0 or num_b < 0:
        raise RuntimeError("Did not find both lines")
    lines[num_a] = lines[num_a].replace(line_a_match.group(1),
                                        line_b_match.group(1))
    lines[num_b] = lines[num_b].replace(line_b_match.group(1),
                                        line_a_match.group(1))
    with open(kanji, 'w') as kf:
        for l in lines:
            kf.write(l)


def swap_strokes(kanji, a, b):
    """Swap strokes in a kanjivg file"""
    # We do hardly any checking. If something is wrong, just blow up.
    with open(kanji) as kf:
        lines = kf.readlines()
    num_a = -1
    num_b = -1
    line_a = ''
    line_b = ''
    line_a_pattern = stroke_text_pattern.format(a)
    line_b_pattern = stroke_text_pattern.format(b)
    for n, l in enumerate(lines):
        if line_a_pattern in l:
            num_a = n
            line_a = l
        if line_b_pattern in l:
            num_b = n
            line_b = l
    if num_a < 0 or num_b < 0:
        raise RuntimeError("Did not find both lines")
    lines[num_a] = line_b.replace(line_b_pattern, line_a_pattern)
    lines[num_b] = line_a.replace(line_a_pattern, line_b_pattern)
    with open(kanji, 'w') as kf:
        for l in lines:
            kf.write(l)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=u"""Swaps data for strokes a and b in the kanjivg svg
file "file".
Select one of the three options, number, data or stroke.
Look at the svg file with a text editor to determine which of the last two
options to use. When both stroke numbers and the strokes themselves are
out of order, run the script twice.""")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--number', action='store_const',
                       const=swap_numbers, dest='function',
                       help=u"""Swap the stroke numbers. Use this  when the
numbers seen are out of order.""")
    group.add_argument('-d', '--data',  action='store_const',
                       const=swap_stroke_data, dest='function',
                       help=u"""Swap only the vector data of the strokes.
Use this when the stroke types are correct in the original file, but the
graphical data doesn't match these types.""")
    group.add_argument('-s', '--stroke', action='store_const',
                       const=swap_strokes, dest='function',
                       help=u"""Swap the whole strokes, including the stroke
type. Use this if the graphical stroke data matches the stroke types in the
original file, but the strokes are in the wrong order.""")
    parser.add_argument('file', type=str, help='Kanji SVG file')
    parser.add_argument('stroke_a', type=int, help='First stroke to swap')
    parser.add_argument('stroke_b', type=int,
                        help='Second stroke to swap with the first stroke')
    args = parser.parse_args()
    args.function(args.file, args.stroke_a, args.stroke_b)
