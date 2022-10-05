import requests
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class KodiRPC:

    def __init__(self, host="localhost", port="8080", user='', password=''):
        self.host = f"http://{host}:{port}/jsonrpc"
        self.headers = {'content-type': 'application/json'}
        self.auth = (user,password)

        r = requests.post(self.host, headers=self.headers, auth=self.auth)
        if (r.status_code == requests.codes.ok) == True:
            logger.info(f"KODI connection to {self.host} successful.")
        else:
            r.raise_for_status()

    def rpcConstructor(self, method="JSONRPC.Introspect", params={}, id=''):
        data={"jsonrpc": "2.0", "method":method, "params":params, "id":id}
        r = requests.post(self.host,
                          headers=self.headers,
                          auth=self.auth,
                          json=data)
        if (r.status_code == requests.codes.ok) == True:
            pass
        else:
            r.raise_for_status()
        return r.json()

    def getApiDocumentation(self):
        x = self.rpcConstructor()
        return x['result']

    def getMovies(self):
        method = 'VideoLibrary.GetMovies'
        params = {'properties': ['playcount', 'file']}
        r = self.rpcConstructor(method=method, params=params)
        return r['result']['movies']

    def getTvShows(self):
        method = 'VideoLibrary.GetTVShows'
        params = {'properties': ['playcount', 'file']}
        r = self.rpcConstructor(method=method, params=params)
        return r['result']['tvshows']

    def getTvEpisodes(self):
        method = 'VideoLibrary.GetEpisodes'
        params = {'properties': ['playcount', 'file', 'tvshowid']}
        r = self.rpcConstructor(method=method, params=params)
        return r['result']['episodes']

    def setWatchedStatus(self, record, watched=True):
        playcount = 1 if watched==True else 0
        if 'movieid' in record.keys():
            method = 'VideoLibrary.SetMovieDetails'
            params = {'movieid': record['movieid'], 'playcount':playcount}
            self.rpcConstructor(method=method, params=params)
        elif 'episodeid' in record.keys():
            method = 'VideoLibrary.SetEpisodeDetails'
            params = {'episodeid':record['episodeid'], 'playcount':playcount}
            self.rpcConstructor(method=method, params=params)
        else:
            logger.error('Not a movie or TV episode.')
