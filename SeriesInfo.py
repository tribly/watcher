#!/usr/bin/env python
# encoding: utf-8

import urllib.request

class SeriesInfo():

    def __init__(self):
        self.search_url = 'http://thetvdb.com/api/GetSeries.php?seriesname='
        self.series_info = 'http://thetvdb.com/api/F8F34A2596D16932/series/'

    def downloadXML(self, url):
        html = urllib.request.urlopen(url)
        data = html.read()

        return data

    def searchSeries(self, name):
        name = name.replace(' ', '%20')

        url = self.search_url + name

        return self.downloadXML(url)

    def getSeriesInfo(self, id):
        url = self.series_info + str(id) + '/all'
        data = self.downloadXML(url)

        return data
