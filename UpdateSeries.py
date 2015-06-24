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
        """@todo: Docstring for getServerTime
        @return: @todo

        """
        time_xml = self.html_handler.getServerTime()
        time_sec = self.xml_handler.extractTime(time_xml)

        return int(time_sec)

    def writeLastUpdateTime(self):
        """Write the current time to the db
        @return: @todo

        """
        time = self.getServerTime()
        self.db_handler.writeTime(time)

    def getSeriesUpdates(self):
        """@todo: Docstring for getSeriesUpdates
        @return: @todo

        """
        last_update = self.db_handler.getLastUpdate()
        updates = self.html_handler.getUpdates(last_update)

        # List containing series and episode updates
        update_list = self.xml_handler.separateSeriesEpisodes(updates)

        # tmp, 'cause where getting a list full of tuples
        local_series_tmp = self.db_handler.getUniqueIDs()
        local_series = []

        # extract the values from the tuples
        for series_id in local_series_tmp:
            local_series.append(series_id[0])

        # Only iterate over series, because we don't need episodes right now
        for series in update_list[0]:
            series_id = int(series)

            # update the info, if a remote series was updated, and found locally
            if series_id in local_series:
                self.updateInfo(series_id)

            break

        self.writeLastUpdateTime()

    def filterSeasons(self, data):
        """Filter out the seasons, so we only have the seasons in the list

        @param data @todo
        @return: @todo

        """
        seasons = []
        season_counter = 1

        for element in data:
            season = int(element[0])

            if season == season_counter:
                seasons.append(season)
                season_counter += 1

        return seasons

    def updateInfo(self, id):
        """Update the info of the local series

        @param series_id @todo
        @return: @todo

        """
        whole_data = self.html_handler.getSeriesInfo(id)
        series_data = self.xml_handler.getSeriesInfo(whole_data)

        local_seasons = self.getLocalSeasons(id)
        remote_seasons = self.extractSeasons(series_data)

        new_seasons = self.compareLocalRemote(local_seasons, remote_seasons)

        # If there are no new seasons, return
        if not new_seasons:
            return

        name = self.db_handler.getNameFromID(id)

        proper_data = self.prepareForDB(name, id, new_seasons, series_data)

        self.db_handler.writeData(proper_data)

    def prepareForDB(self, name, series_id, new_seasons, remote_data):
        """Prepare the data to be handled properly by the db

        @param name @todo
        @param new_seasons @todo
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

        @param data @todo
        @return: @todo

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

