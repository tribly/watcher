#!/usr/bin/env python
# encoding: utf-8

import sqlite3
import os.path

class Database():

    def __init__(self):
        self.connection = self.checkForDB()

    def checkForDB(self):
        if not os.path.isfile('./series.db'):
            return self.createDB()
        else:
            return sqlite3.connect('series.db')

    def closeDB(self):
        self.connection.close()

    def getNext(self, id):
        cursor = self.connection.cursor()
        id = (id,)

        cursor.execute('''SELECT name, series_id, season, episode
                        FROM info
                        WHERE seen = 0
                        AND series_ID = ?
                        ORDER BY date asc, episode asc''', id)

        return cursor.fetchone()

    def getNextID(self, id):
        cursor = self.connection.cursor()

        cursor.execute('''SELECT id
                        FROM info
                        WHERE seen = 0
                        AND series_ID = ?
                        ORDER BY date asc, episode asc''', id)

        return cursor.fetchone()

    def getUniqueIDs(self):
        cursor = self.connection.cursor()

        cursor.execute('SELECT DISTINCT series_ID FROM info')

        return cursor.fetchall()

    def writeData(self, data):
        cursor = self.connection.cursor()

        proper = []

        # Convert all string-list to db handable tuple
        for element in data:
            element[0] = str(element[0])
            element[1] = int(element[1])
            element[2] = int(element[2])
            element[3] = int(element[3])
            element[4] = str(element[4])

            proper.append(tuple(element))

        cursor.executemany('INSERT INTO info VALUES(NULL, ?, ?, ?, ?, ?, 0)', proper)
        self.connection.commit()

    def extractName(self, data):
        pos = data.find('-')

        return data[:pos - 1]

    def getIdFromName(self, name):
        cursor = self.connection.cursor()
        name = (name,)

        cursor.execute('''SELECT series_id
                          FROM info
                          WHERE name = ?''', name)

        series_id = cursor.fetchone()
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

    def createDB(self):
        connection = sqlite3.connect('series.db')
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE "info" (
                          "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                          "name" TEXT NOT NULL,
                          "series_id" INTEGER NOT NULL,
                          "season" INTEGER NOT NULL,
                          "episode" INTEGER NOT NULL,
                          "date" TEXT NOT NULL,
                          "seen" INTEGER NOT NULL
                          )''')

        connection.commit()
        return connection
