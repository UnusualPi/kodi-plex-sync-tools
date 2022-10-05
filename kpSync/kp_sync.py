from kodiRpc.kodiRpc import KodiRPC
from plexApi.plexApi import PlexAPI
from pathlib import PurePath
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class kpSync:

    def __init__(self,plexHost='',plexToken='',kodiHost='',kodiPort='',
                 kodiUser='',kodiPassword=''):
        self.plex = PlexAPI(plexHost, token=plexToken)
        self.kodi = KodiRPC(kodiHost, kodiPort, user=kodiUser, password=kodiPassword)

    def setLogLevel(level):
        if level.lower() == 'info':
            logger.setLevel(logging.INFO)
        elif level.lower() == 'debug':
            logger.setLevel(logging.DEBUG)
        elif level.lower() == 'warning':
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.ERROR)

    def getParentPath(self, fullPath):
        """Captures filename with immediate parent directory.  This will be used
        for matching between Kodi and Plex"""
        pp = PurePath(fullPath)
        return pp.parent.name + '/' + pp.name

    def matchRecords(self, whichRecords='all'):
        """
        |----------------------------------------------------------------------
        | Matches records between Kodi and Plex libraries.
        |
        | Parameters
        |----------------------------------------------------------------------
        | whichRecords : str, default 'all'
        |   'all' will return both movies and episodes
        |   'movies' will return movies
        |   'episodes' will return episodes
        |----------------------------------------------------------------------
        """
        if whichRecords=='movies':
            kodiRecords = self.kodi.getMovies()
            plexRecords = self.plex.getMovies()
        elif whichRecords=='episodes':
            kodiRecords = self.kodi.getTvEpisodes()
            plexRecords = self.plex.getTvEpisodes()
        else:
            kodiRecords = self.kodi.getTvEpisodes() + self.kodi.getMovies()
            plexRecords = self.plex.getTvEpisodes() + self.plex.getMovies()

        allSlugs = []
        for pr in plexRecords:
            for location in pr.locations:
                slug = {}
                slug['slug'] = self.getParentPath(location)
                slug['plexRecord'] = pr
                slug['plexWatched'] = pr.isPlayed
                slug['kodiRecord'] = None
                slug['kodiWatched'] = None
                allSlugs.append(slug)

        for kr in kodiRecords:
            matched=0
            kodiSlug = self.getParentPath(kr['file'])
            for slug in allSlugs:
                if kodiSlug == slug['slug']:
                    slug['kodiRecord'] = kr
                    slug['kodiWatched'] = True if kr['playcount'] > 0 else False
                    matched=1

            if matched == 0:
                allSlugs.append({'slug':kodiSlug,
                                'plexRecord': None,
                                'plexWatched': None,
                                'kodiRecord': kr,
                                'kodiWatched': True if kr['playcount'] > 0 else False})
        payload = {'allRecords':allSlugs,
                   'watchedStatusNotSynced': [s for s in allSlugs if s['plexWatched'] != s['kodiWatched'] and s['plexWatched'] != None and s['kodiWatched'] != None],
                   'onPlexOnly': [s for s in allSlugs if s['kodiRecord'] == None],
                   'onKodiOnly': [s for s in allSlugs if s['plexRecord'] == None]
                   }
        logger.info(f"""{len(payload['allRecords'])} Total records.\n{len(payload['watchedStatusNotSynced'])} out of Sync.\n{len(payload['onPlexOnly'])} on Plex ONLY.\n{len(payload['onKodiOnly'])} on Kodi ONLY.""")
        return payload

    def match_and_sync(self, whichRecords='all', direction='sync'):
        """
        |----------------------------------------------------------------------
        | Execute the matchRecords() fucntion and indicated sync function with
        | no prompts.
        |
        |
        | Parameters
        |----------------------------------------------------------------------
        | whichRecords : str, default 'all'
        |   'all' will return both movies and episodes
        |   'movies' will return movies
        |   'episodes' will return episodes
        |
        | direction : str, default 'sync'
        |   'sync' execute `sync_watched(self, payload)``
        |   'kodi_to_plex' execute `force_kodi_to_plex(self,payload)`
        |   'plex_to_kodi' execute `force_plex_to_kodi(self, payload)`
        |----------------------------------------------------------------------
        """
        payload = self.matchRecords(whichRecords=whichRecords)
        if direction == 'sync':
            self.sync_watched(payload['watchedStatusNotSynced'])
        elif direction == 'kodi_to_plex':
            self.force_kodi_to_plex(payload['allRecords'])
        elif direction == 'plex_to_kodi':
            self.force_plex_to_kodi(payload['allRecords'])

    def sync_watched(self, payload):
        """
        |----------------------------------------------------------------------
        | Will update the watched status on either Plex or Kodi.  This will ONLY
        | mark records as watched, it will not mark records as unwatched.
        | Neither Kodi or Plex provide a timestamp for watched status changes.
        |
        | Parameters
        |----------------------------------------------------------------------
        | payload : list
        |   List of dicts provided by the matchRecords() function.  Either from
        |   the "allRecords" key or the 'watchedStatusNotSynced' key.
        |----------------------------------------------------------------------
        """
        for r in payload:
            if r['plexWatched'] == True and r['kodiWatched'] == False and r['plexWatched'] != None and r['kodiWatched'] != None:
                self.kodi.setWatchedStatus(r['kodiRecord'], watched=True)
                logger.info(f"Marked {r['slug']} watched on Kodi.")
            elif r['plexWatched'] == False and r['kodiWatched'] == True and r['plexWatched'] != None and r['kodiWatched'] != None:
                self.plex.setWatchedStatus(r['plexRecord'], watched=True)
                logger.info(f"Marked {r['slug']} watched on Plex.")
        logger.info("Update complete.")

    def force_kodi_to_plex(self,payload):
        """
        |----------------------------------------------------------------------
        | Will update the watched status on Plex using Kodi watched statuses.
        | This will mark records either Played or Unplayed in the Plex Library.
        |
        | Parameters
        |----------------------------------------------------------------------
        | payload : list
        |   List of dicts provided by the matchRecords() function.  Either from
        |   the "allRecords" key or the 'watchedStatusNotSynced' key.
        |----------------------------------------------------------------------
        """
        for r in payload:
            if r['plexWatched'] != r['kodiWatched'] and r['plexWatched'] != None and r['kodiWatched'] != None:
                self.plex.setWatchedStatus(r['plexRecord'], watched = r['kodiWatched'])
                logger.info(f"Marked {r['slug']} Plex watched status to {r['kodiWatched']}")
        logger.info("Update complete.")

    def force_plex_to_kodi(self,payload):
        """
        |----------------------------------------------------------------------
        | Will update the watched status on Kodi using Plex played statuses.
        | This will mark records either watched or unwatched in the Kodi Library.
        |
        | Parameters
        |----------------------------------------------------------------------
        | payload : list
        |   List of dicts provided by the matchRecords() function.  Either from
        |   the "allRecords" key or the 'watchedStatusNotSynced' key.
        |----------------------------------------------------------------------
        """
        for r in payload:
            if r['plexWatched'] != r['kodiWatched'] and r['plexWatched'] != None and r['kodiWatched'] != None:
                self.kodi.setWatchedStatus(r['kodiRecord'], watched = r['plexWatched'])
                logger.info(f"Marked {r['slug']} Kodi watched status to {r['plexWatched']}")
        logger.info("Update complete.")
