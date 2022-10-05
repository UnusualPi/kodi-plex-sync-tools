import os
import json
import sqlite3
import pymysql
import itertools

def mysqlConn(db):
    mysql_config = json.load(open(r'mysqlConfig.json'))
    mysql_config['db'] = db
    conn = pymysql.connect(**mysql_config)
    return conn

def sqlConn(db):
    # this creates a dict output like mysql dictcursor
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    conn = sqlite3.connect(db)
    conn.row_factory = dict_factory
    return conn

def getMysqlVideoFiles(conn):
    cur = pymysql.cursors.DictCursor(conn)
    cur.execute("SELECT * FROM files JOIN path ON path.idPath = files.idPath")
    r = cur.fetchall()
    return r

def getSqlVideoFiles(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM files JOIN path ON path.idPath = files.idPath")
    r = cur.fetchall()
    return r

def sanitizeValues(value):
    if isinstance(value, (int,float)) == True:
        return value
    elif value == None:
        return 'NULL'
    else:
        return '"{}"'.format(value)

def matchVideos(sourceDb, destinationDb):
    superSet = []
    for (l,r) in zip(sourceDb,destinationDb):
        superSet.append(l['strPath'] + l['strFilename'].lower())
        superSet.append(r['strPath'] + r['strFilename'].lower())
    superSet = list(set(superSet))
    superSetDict = {}
    for video in superSet:
        file = {video:{'sourceDb':{},'destinationDb':{}}}
        for v in sourceDb:
            if (v['strPath'] + v['strFilename']).lower() == video.lower():
                file[video]['sourceDb'] = v
                break
        for v in destinationDb:
            if (v['strPath'] + v['strFilename']).lower() == video.lower():
                file[video]['destinationDb'] = v
                break
        superSetDict.update(file)
    return superSetDict

def generatePlayCountQuery(videoPayload):
    q = """UPDATE files SET playCount = {playCount}, lastPlayed = {lastPlayed}, dateAdded = {dateAdded} WHERE idFile = {idFile}"""
    queries = []
    for k,v in videoPayload.items():
        d = {'playCount':sanitizeValues(v['sourceDb'].get('playCount')),
                'lastPlayed':sanitizeValues(v['sourceDb'].get('lastPlayed')),
                'dateAdded':sanitizeValues(v['sourceDb'].get('dateAdded')),
                'idFile': sanitizeValues(v['destinationDb'].get('idFile'))}
        if d['idFile'] != None:
            queries.append(q.format(**d))
    return queries

def updatePlayCount(conn, queries):
    cur = conn.cursor()
    for q in queries:
        cur.execute(q)
    conn.commit()
