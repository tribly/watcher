#!/usr/bin/env python
# encoding: utf-8

import sqlite3
import os.path

class Database():

    def __init__(self):
        self.connection = self.checkForDB()

    def checkForDB(self):
        if not os.path.isfile('./series.db'):
            self.createDB()
        else:
            return sqlite3.connect('series.db')

    def closeDB(self):
        self.connection.close()

    def getNext(self, id):
        cursor = self.connection.cursor()

        cursor.execute("SELECT name, season, episode\
                        FROM info\
                        WHERE seen = 0")

        # TODO: fetch proper one
        data = cursor.fetchone()
        return data

    def writeData(self, data):
        cursor = self.connection.cursor()

        proper = []

        for element in data:
            element[0] = str(element[0])
            element[1] = int(element[1])
            element[2] = int(element[2])
            element[3] = int(element[3])
            element[4] = str(element[4])

            proper.append(tuple(element))

        cursor.executemany('INSERT INTO info VALUES(NULL, ?, ?, ?, ?, ?, 0)', proper)
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
