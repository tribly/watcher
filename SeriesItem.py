#!/usr/bin/env python
# encoding: utf-8

import tkinter

class SeriesItem():

    def __init__(self, name, season, episode):
        self.name = name
        self.season = season
        self.episode = episode

        self.info = self.concSeasonEpisode(self.name, self.season, self.episode)

    def concSeasonEpisode(self, name, season, episode):
        info = name + " - s" + str(season) + "e" + str(episode)
        return info

    def getInfo(self):
        return self.info
