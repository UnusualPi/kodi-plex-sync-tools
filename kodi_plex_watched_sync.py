from kpSync.kp_sync import kpSync
import json
#kpSync.setLogLevel('DEBUG')

kpAuth = json.load(open(r'kodiPlexConfig.json'))
sync = kpSync(**kpAuth)

sync.match_and_sync(whichRecords='all', direction ='sync')
