#!/usr/bin/env python
# encoding: utf-8

import urllib.request

class SeriesInfo():

    def __init__(self):
        self.api_key = 'F8F34A2596D16932'
        self.search_url = 'http://thetvdb.com/api/GetSeries.php?seriesname='
        self.series_info = 'http://thetvdb.com/api/%s/series/' % self.api_key
        self.episode_info = 'http://thetvdb.com/api/%s/episodes/' % self.api_key
        self.get_time = 'http://thetvdb.com/api/Updates.php?type=none'
        self.updates = 'http://thetvdb.com/api/Updates.php?type=all&time='

    def downloadXML(self, url):
        html = urllib.request.urlopen(url)
        data = html.read()

        return data

    def getServerTime(self):
        """Get the current server time
        @return: @todo

        """
        html = urllib.request.urlopen(self.get_time)
        data = html.read()

        return data

    def getUpdates(self, time):
        """Download the updates since time

        @param time - int
        @return: @todo

        """
        url = self.updates + str(time)
        html = urllib.request.urlopen(url)
        data = html.read()

        return data

    def searchSeries(self, name):
        name = name.replace(' ', '%20')

        url = self.search_url + name

        return self.downloadXML(url)

    def getEpisodeInfo(self, episode_id):
        """Fetch the info for the given episode

        @param episode_id @todo
        @return: @todo

        """
        url = self.episode_id + str(episode_id)
        data = self.downloadXML(url)

        return data

    def getSeriesInfo(self, id):
        url = self.series_info + str(id) + '/all'
        data = self.downloadXML(url)

        return data
