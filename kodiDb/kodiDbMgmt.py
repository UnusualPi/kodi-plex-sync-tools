import kodiDbHelper as kodi

mysqlConn = kodi.mysqlConn('kodivideo119')
sqliteDir = r'\\MEDIACENTER-LR\Kodi App Data\userdata\Database'
sqlConn = kodi.sqlConn(sqliteDir+'\MyVideos119.db')
mysqlVideos = kodi.getMysqlVideoFiles(mysqlConn)

mysqlVideos

for v in mysqlVideos:
    print(v['strPath'])
    #v['strPath'] = v['strPath'].replace('MIKESERV', 'MIKESERV.localdomain')

kodiDbVideos = kodi.getSqlVideoFiles(sqlConn)
for v in kodiDbVideos:
    print(v['strPath'])

allVideoDict = kodi.matchVideos(sourceDb=mysqlVideos
                                , destinationDb=kodiDbVideos)

updateQueries = kodi.generatePlayCountQuery(allVideoDict)
updateQueries[0]

kodi.updatePlayCount(mysqlConn, updateQueries)
## Update resume position is in the "bookmarks" table

sqlConn.close()
mysqlConn.close()
