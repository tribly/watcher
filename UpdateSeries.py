#!/usr/bin/env python
# encoding: utf-8

import threading

from SeriesInfo import SeriesInfo
from XMLParser import XMLParser
from Database import Database

class UpdateSeries(threading.Thread):
    """Update the series at startup"""

    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller
        self.html_handler = SeriesInfo()
        self.xml_handler = XMLParser()
        self.db_handler = Database()

    def run(self):
        self.controller.updateStatus('updating series')
        self.getSeriesUpdates()
        self.controller.updateStatus('done updating series')

    def getServerTime(self):
        """Get the current time from the server

        @return: int - time in seconds

        """
        time_xml = self.html_handler.getServerTime()
        time_sec = self.xml_handler.extractTime(time_xml)

        return int(time_sec)

    def writeLastUpdateTime(self):
        """Write the current time to the db

        """
        time = self.getServerTime()
        self.db_handler.writeTime(time)

    def getSeriesUpdates(self):
        """Fetch the new updates

        """
        last_update = self.db_handler.getLastUpdate()
        updates = self.html_handler.getUpdates(last_update)

        # List containing series and episode updates
        update_list = self.xml_handler.separateSeriesEpisodes(updates)

        # series ids we have locally in our db
        local_series = self.db_handler.getUniqueIDs()
        # episode ids we have locally in our db
        local_episodes = self.db_handler.getEpisodeIDs()

        # Only iterate over series, because we don't need episodes right now
        # update_list[0] contains series
        # update_list[1] contains episodes
        for series in update_list[0]:
            series_id = int(series)

            # update the info, if a remote series was updated, and found locally
            if series_id in local_series:
                self.updateInfo(series_id)

        for episode in update_list[1]:
            episode_id = int(episode)

            if episode_id in local_episodes:
                self.updateEpisode(episode_id)

        self.writeLastUpdateTime()

    def updateEpisode(self, episode_id):
        """Update the episode with the proper id

        """
        whole_data = self.html_handler.getSeriesInfo(episode_id)
        episode_data = self.xml_handler.getSeriesInfo(whole_data)

        self.db_handler.updateEpisodeDate(episode_id, episode_data[1])

    def filterSeasons(self, data):
        """Filter out the seasons, so we only have the seasons in the list

        @param data - list : list full of info
        @return: seasons - list : list of distinct seasons

        """
        seasons = []
        season_counter = 1

        for element in data:
            season = int(element[0])

            if season == season_counter:
                seasons.append(season)
                season_counter += 1

        return seasons

    def updateInfo(self, series_id):
        """Update the info of the local series

        @param series_id - int : id of series
        @return: nothing

        """
        whole_data = self.html_handler.getSeriesInfo(series_id)
        series_data = self.xml_handler.getSeriesInfo(whole_data)

        local_seasons = self.getLocalSeasons(series_id)
        remote_seasons = self.extractSeasons(series_data)

        new_seasons = self.compareLocalRemote(local_seasons, remote_seasons)

        # If there are no new seasons, return
        if not new_seasons:
            return

        name = self.db_handler.getNameFromID(series_id)
        proper_data = self.prepareForDB(name, series_id, new_seasons, series_data)

        self.db_handler.writeData(proper_data)

    def prepareForDB(self, name, series_id, new_seasons, remote_data):
        """Prepare the data to be handled properly by the db

        @param name - string : Name of the series
        @param new_seasons - list : List of seasons to add
        @return: Final list, which the db can process

        """
        episodes = []

        for season in new_seasons:
            for e in remote_data:
                if season == int(e[0]):
                    episodes.append(e)

        whole_data = self.constructDBData(name, series_id, episodes)

        return whole_data

    def extractSeasons(self, data):
        """Extract only the season information

        @param data - list : list of info
        @return: seasons - list :

        """
        seasons = []

        for e in data:
            season = int(e[0])
            if season not in seasons:
                seasons.append(season)

        return seasons

    def constructDBData(self, name, series_id, data):
        """Concstruct the list, so that the db can write it properly

        @param name @todo
        @param data @todo
        @return: @todo

        """
        series_data = []

        for e in data:
            series_data.append([name, series_id] + e)

        return series_data

    def getLocalSeasons(self, series_id):
        """Get the local seasons already in db

        @param id @todo
        @return: @todo

        """
        seasons = self.db_handler.getSeasons(series_id)

        return seasons

    def compareLocalRemote(self, local, remote):
        """Compare both local and remote seaons. If there is a remote season
        not present locally, add it to the db

        @param local list of localy available seasons
        @param remote list of remotely available seasons
        @return: @todo

        """
        # compare the 2 series seasons and add the new seasons to the array
        new_seasons = list(set(remote) - set(local))

        return new_seasons

