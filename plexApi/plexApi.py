""" Plex API License https://github.com/pkkid/python-plexapi:
Copyright (c) 2010, Michael Shepanski
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name python-plexapi nor the names of its contributors
      may be used to endorse or promote products derived from this software without
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from plexapi.server import PlexServer
from pathlib import PurePath
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class PlexAPI:

    def __init__(self, host='127.0.0.1', port='32400', token=''):
        self.host = f"http://{host}:{port}"
        self.token = token
        self.client = PlexServer(self.host, self.token)
        logger.info(f"PLEX connection to {self.host} successful.")

    def getMovies(self):
        return self.client.library.section('Movies').all()

    def getTvShows(self):
        return self.client.library.section('Tv Shows').all()

    def getTvEpisodes(self):
        shows = self.client.library.section('Tv Shows').all()
        episodes = []
        for show in shows:
            episodes = episodes + show.episodes()
        return episodes

    def setWatchedStatus(self, record, watched=True):
        if watched==True:
            record.markPlayed()
        else:
            record.markUnplayed()
