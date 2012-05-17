#!/usr/bin/python2

# create_db.py creates an sqlite database containing kanjivg data
# Copyright 2012 Cayenne Boyer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3
import os
from xml.etree.ElementTree import ElementTree
import codecs
import argparse

tables = {
'kanji': u'''
CREATE TABLE kanji (
    character TEXT,         -- the character, in utf-8
    variant TEXT,           -- string describing the variant
    svg TEXT,               -- full svg text
    PRIMARY KEY (character, variant)
)
''',
'component': u'''
CREATE TABLE component (
    parent,                 -- primary character, in utf-8
    child,                  -- a character that's a direct component
    UNIQUE (parent, child)
)
'''}

parser = argparse.ArgumentParser(description='Create a database of '
                                 'kanjivg data',
                                 epilog='See table schemas for '
                                 'information on database contents')
parser.add_argument('--svg-dir', 
                    help='location of directory containing svgs '
                    '(default: %(default)s)',
                    dest='src_dir',
                    default=os.path.join(os.path.dirname(__file__),
                                         'kanji'))
parser.add_argument('--out', 
                    help='database file to write to; note that any '
                    'file in this location will be overwritten '
                    '(default: %(default)s)',
                    metavar='OUT.DB',
                    dest='db_file',
                    default='kanjivg.db')
parser.add_argument('--drop-variants',
                    help="don't include variants such as Kaisho in the "
                    'database (default: %(default)s)',
                    action='store_true')
parser.add_argument('--tables',
                    help="include only those tables listed "
                    "(all tables by default: %(default)s)",
                    default=tables.keys(),
                    nargs='+',
                    metavar='TABLE'
                    )

def create_database(args=parser.parse_args([])):
    """Create a sqlite3 database out of the data in the kanjivg svgs

    Takes an optional namespace argument with argparser args;
    otherwise uses the argparser defaults
    
    """
    # create a new database and connect to it; note that this method
    # will not update the database for any other active connections
    if os.path.exists(args.db_file):
        os.remove(args.db_file)
    conn = sqlite3.connect(args.db_file)
    cur = conn.cursor()
    # create tables
    for t in args.tables:
        cur.execute(tables[t])
    # create xml element tree
    tree = ElementTree()
    # process the data
    for src_filename in os.listdir(args.src_dir):
        kanji = {}
        # get the character and variant name from the file name
        cv = src_filename.replace('.svg','').split('-') + ['']
        kanji['character'] = unichr(int(cv[0], 16))
        kanji['variant'] = unicode(cv[1], 'utf-8')
        # read the file to get the svg
        with codecs.open(os.path.join(args.src_dir, src_filename), 
                        'r', 'utf-8') as f:
            kanji['svg'] = f.read()
        # get the components out of the svg
        tree.parse(os.path.join(args.src_dir, src_filename))
        cgs = tree.findall('/'.join(['{http://www.w3.org/2000/svg}g']*3))
        components = [s.attrib['{http://kanjivg.tagaini.net}element'] 
                      for s in cgs if
                      '{http://kanjivg.tagaini.net}element' in s.keys()]
        # write to database
        if 'kanji' in args.tables:
            if kanji['variant'] == '' or args.drop_variants == False:
                cur.execute(u'INSERT INTO kanji VALUES '
                            u'(:character, :variant, :svg)', kanji)
        if 'component' in args.tables:
            if kanji['variant'] == '':
                for c in components:
                    cur.execute(u'INSERT OR IGNORE INTO component '
                                u'VALUES (?, ?)', 
                                (kanji['character'], c))
    conn.commit()

if __name__ == "__main__":
    args = parser.parse_args()
    create_database(args)
