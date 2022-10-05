from kpSync.kp_sync import kpSync
import json
#kpSync.setLogLevel('DEBUG')

kpAuth = json.load(open(r'kodiPlexConfig.json'))
sync = kpSync(**kpAuth)

help(kpSync.match_and_sync)


episodes = sync.matchRecords(whichRecords='episodes')
movies = sync.matchRecords(whichRecords='movies')
all = episodes = sync.matchRecords(whichRecords='all')

sync.match_and_sync()
