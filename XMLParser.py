#!/usr/bin/env python
# encoding: utf-8

import xml.etree.ElementTree as ET

class XMLParser():

    def __init__(self):
        pass

    def getSeriesInfo(self, data):
        # TODO: ET.parse to ET.fromstring
        root = ET.fromstring(data)
        series_info = []
        season = 1

        episodes = root.findall('Episode')

        for parent in episodes:
            cur_season = parent.find('SeasonNumber').text

            if cur_season == '0':
                continue

            if cur_season != season:
                season = cur_season

            info = [season]

            info.append(parent.find('EpisodeNumber').text)
            info.append(parent.find('FirstAired').text)

            series_info.append(info)

        return series_info

    def searchSeries(self, xml):
        root = ET.fromstring(xml)

        series = root.findall('Series')

        series_dict = {}

        if len(series)  == 1:
            name = series[0].find('SeriesName').text
            id = series[0].find('id').text

            series_dict[name] = id

        for child in series:
            name = child.find('SeriesName').text
            id = child.find('id').text
            series_dict[name] = id

        return series_dict

