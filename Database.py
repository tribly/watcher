#!/usr/bin/env python
# encoding: utf-8

import sqlite3
import os.path
from datetime import datetime
import time

class Database():

    def __init__(self):
        self.connection = self.checkForDB()

    def checkForDB(self):
        if not os.path.isfile('./series.db'):
            return self.createDB()
        else:
            return sqlite3.connect('series.db', check_same_thread=False)

    def closeDB(self):
        self.connection.close()

    def writeTime(self, time):
        """Write the last update time to db

        @param time - int - in sec

        """
        cursor = self.connection.cursor()
        time = (time,)

        cursor.execute('''UPDATE conf
                          set last_update = ?''', time)

        self.connection.commit()
        cursor.close()

    def extractValues(self, data):
        """Extract the values from the tuples inside a string

        @param data @todo
        @return: @todo

        """
        out = []
        for i in data:
            out.append(i[0])

        return out

    def getNext(self, id):
        cursor = self.connection.cursor()
        id = (id,)

        cursor.execute('''SELECT name, series_id, season, episode, date
                        FROM info
                        WHERE seen = 0
                        AND series_ID = ?
                        ORDER BY date asc, episode asc''', id)

        data = cursor.fetchone()

        cursor.close()
        return data

    def getNextID(self, id):
        cursor = self.connection.cursor()

        cursor.execute('''SELECT id
                        FROM info
                        WHERE seen = 0
                        AND series_ID = ?
                        ORDER BY date asc, episode asc''', id)

        data = cursor.fetchone()

        cursor.close()
        return data

    def getEpisodeIDs(self):
        """Get the ids from all episodes in the db
        @return: @todo

        """
        cursor = self.connection.cursor()

        cursor.execute('SELECT episode_id FROM info')

        data = cursor.fetchall()
        data = self.extractValues(data)

        cursor.close()
        return data

    def getUniqueIDs(self):
        cursor = self.connection.cursor()

        cursor.execute('SELECT DISTINCT series_ID FROM info')

        data = cursor.fetchall()
        data = self.extractValues(data)

        cursor.close()
        return data

    def getSeasons(self, series_id):
        """Get all seasons from a specific series

        @param series_id @todo
        @return: @todo

        """
        cursor = self.connection.cursor()
        series_id = (series_id,)

        cursor.execute('''SELECT season
                          FROM info
                          WHERE series_id = ?''', series_id)
        seasons = []

        for season in cursor.fetchall():
            if season[0] not in seasons:
                seasons.append(season[0])

        cursor.close()
        return seasons

    def writeData(self, data):
        """Write the data to the db

        @param data [name, id, season, episode, air_date]
        @return: @todo

        """
        cursor = self.connection.cursor()

        proper = []

        # Convert all string-list to db handable tuple
        for element in data:
            element[0] = str(element[0])
            element[1] = int(element[1])
            element[2] = int(element[2])
            element[3] = int(element[3])
            element[4] = int(element[4])
            element[5] = str(element[5])

            proper.append(tuple(element))

        cursor.executemany('''INSERT INTO info
                              VALUES(NULL, ?, ?, ?, ?, ?, ?, 0)''', proper)
        self.connection.commit()
        cursor.close()

    def getNameFromID(self, series_id):
        """Get the name from the id

        @param name @todo
        @return: @todo

        """
        cursor = self.connection.cursor()
        series_id = (series_id,)

        cursor.execute('''SELECT name
                          FROM info
                          WHERE series_id = ?''', series_id)


        data = cursor.fetchone()

        cursor.close()
        return data

    def extractName(self, data):
        pos = data.find('-')

        if pos == -1:
            return data

        return data[:pos - 1]

    def writeBulkData(self, name, data):
        # data = [[],[],...]
        cursor = self.connection.cursor()
        id = self.getIdFromName(name)
        id = id[0]
        season = 1
        episode = 1

        for s in data:
            for e in s:
                string = '''UPDATE info
                            SET seen = %d
                            WHERE series_id = %d
                            AND season = %d
                            AND episode = %d''' % (e, id, season, episode)
                cursor.execute(string)
                episode += 1
            season += 1
            episode = 1

        self.connection.commit()
        cursor.close()

    def checkForSeason(self, season, series_id):
        """Check if the season is present in the series

        @param season - int
        @param series_id - int
        @return: @todo

        """
        cursor = self.connection.cursor()

        data = (season,series_id )

        cursor.execute('''SELECT season
                          FROM info
                          WHERE season = ?
                          AND series_id = ?''', data)

        if cursor.fetchone() == None:
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def getIdFromName(self, name):
        cursor = self.connection.cursor()
        name = (name,)

        cursor.execute('''SELECT series_id
                          FROM info
                          WHERE name = ?''', name)

        series_id = cursor.fetchone()

        cursor.close()
        return series_id

    def setWatched(self, name):
        cursor = self.connection.cursor()
        name = self.extractName(name)
        id = self.getIdFromName(name)

        next_ = self.getNextID(id)

        cursor.execute('''UPDATE info
                          SET seen = 1
                          WHERE id = ?''', next_)
        self.connection.commit()
        cursor.close()

    def getSeasonEpisodeData(self, name):
        cursor = self.connection.cursor()
        name = self.extractName(name)
        id = self.getIdFromName(name)

        cursor.execute('''SELECT season
                          FROM info
                          WHERE series_id = ?
                          ORDER BY season DESC''', id)

        nr_seasons = cursor.fetchone()[0]
        data = []

        for season in range(nr_seasons):
            data.append([])
            season_ = (id[0], season + 1)
            cursor.execute('''SELECT seen
                              FROM info
                              WHERE series_id = ?
                              AND season = ?
                              ORDER BY episode ASC''', season_)

            nr_episodes = cursor.fetchall()

            for e in nr_episodes:
                data[season].append(e[0])

        cursor.close()
        return data

    def getLastUpdate(self):
        cursor = self.connection.cursor()

        cursor.execute('''SELECT last_update
                          FROM conf
                       ''')

        data = cursor.fetchone()

        cursor.close()
        return data

    def updateEpisodeDate(self, episode_id, date):
        """Update the date for the given episode

        """
        cursor = self.connection.cursor()

        data = (int(episode_id), str(date))

        cursor.execute('''UPDATE info
                          SET date = ?
                          WHERE episode_id = ?''', data)

        self.connection.commit()
        cursor.close()

    def createDB(self):
        connection = sqlite3.connect('series.db')
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE "info" (
                          "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                          "name" TEXT NOT NULL,
                          "series_id" INTEGER NOT NULL,
                          "season" INTEGER NOT NULL,
                          "episode_id" INTEGER NOT NULL,
                          "episode" INTEGER NOT NULL,
                          "date" TEXT NOT NULL,
                          "seen" INTEGER NOT NULL
                          )''')

        cursor.execute('''CREATE TABLE "conf" (
                          "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                          "last_update" INTEGER
                          )''')

        t = (datetime.now() - datetime(1970,1,1)).total_seconds()


        cursor.execute('''INSERT INTO conf
                          VALUES (NULL, ?)''', (t,))

        connection.commit()
        cursor.close()
        return connection
