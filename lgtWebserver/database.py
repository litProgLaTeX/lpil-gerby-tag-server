
import logging
import os
import sqlite3
import sys
import yaml

class LabelDatabase(object) :

  def __init__(self, dbName, dbConf) :
    self.dbName = dbName
    self.dbConf = dbConf
    self.log    = logging.getLogger(dbName)
    if 'logLevel' in dbConf :
      self.log.setLevel(dbConf['logLevel'])

    if 'dbPath' not in self.dbConf :
      self.dbConf['dbPath'] = f"{self.dbName}.sqlite"
    newDB = False
    dbPath = self.dbConf['dbPath']
    self.dbPath = dbPath
    self.log.info(f"Connecting to {dbPath}")
    if not os.path.isfile(dbPath) :
      self.log.critical(f"Could not find the {dbName} database ({dbPath})")
      self.log.critical(f"The {dbName} database MUST be created before running the webserver")
      self.log.info(f"You can create the {dbName} database using the `lgtImporter` script")
      sys.exit(1)

  def update(self, label, desc, inuse) :
    #print(label, desc, inuse)
    with sqlite3.connect(self.dbPath) as con :
      cur = con.cursor()
      try :
        cur.execute(
          "INSERT INTO labels (label, desc, inuse) VALUES(?,?,?)", (label, desc, inuse)
        )
        cur.execute(
          "INSERT INTO labelsfts (label, desc) VALUES(?,?)", (label, desc)
        )
      except sqlite3.IntegrityError :
        cur.execute(
          f"UPDATE labels SET desc='{desc}', inuse='{inuse}' WHERE label = '{label}'"
        )
        cur.execute(
          f"UPDATE labelsfts SET desc='{desc}' WHERE label = '{label}'"
        )

  def findLabel(self, label) :
    theRows = []
    with sqlite3.connect(self.dbPath) as con :
      res = con.cursor().execute(
        f"SELECT tag, label, desc, inuse FROM labels WHERE labels.label = '{label}'"
      )
      for aRow in res :
        theRows.append({
          'tag'   : aRow[0],
          'label' : aRow[1],
          'desc'  : aRow[2],
          'inuse' : aRow[3]
        })
        break # we only want the first one!
    return theRows

  def searchKeywords(self, searchQuery) :
    theRows = []
    with sqlite3.connect(self.dbPath) as con :
      # see: https://www.sqlitetutorial.net/sqlite-full-text-search/
      res = con.cursor().execute(
        f"SELECT label, desc FROM labelsfts WHERE labelsfts MATCH '{searchQuery}'"
      )
      for aRow in res :
        theRows.append({
          'label'  : aRow[0],
          'desc'  : aRow[1],
        })
    return theRows
