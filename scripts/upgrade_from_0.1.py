#!/usr/bin/env python3
# vim:fileencoding=utf-8

import os, sys
import sqlite3
import configparser
import pickle
import logging

from myutils import enable_pretty_logging
enable_pretty_logging(logging.DEBUG)

top_dir = os.path.normpath(os.path.join(__file__, '../..'))
sys.path.append(top_dir)

import pkgreader
from dbutil import *

def main(conffile):
  config = configparser.ConfigParser()
  config.read(conffile)
  config = config['repository']

  base = config.get('path')
  dbname = config.get('info-db', os.path.join(base, 'pkginfo.db'))
  db = sqlite3.connect(dbname, isolation_level=None)
  assert getver(db) == '0.1', 'wrong database version'
  input('Please stop the service and then press Enter.')
  try:
    db.execute('alter table pkginfo add info text')
  except sqlite3.OperationalError:
    # the column is already there
    pass
  pkgs = [x[0] for x in db.execute('select filename from pkginfo')]
  for p in pkgs:
    try:
      info = pkgreader.readpkg(p)
    except:
      logging.error('failed to read info for package %s', act.path)
      info = None
    info = pickle.dumps(info)
    db.execute('update pkginfo set info=?', (info,))
  setver(db, '0.2')
  db.close()

  input('Please re-start the service with new code and then press Enter.')

if __name__ == '__main__':
  main(sys.argv[1])
