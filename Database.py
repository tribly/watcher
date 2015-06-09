#!/usr/bin/env python
# encoding: utf-8

import sqlite3

class Database():

    def __init__(self):
        self.connection = sqlite3.connect('series.db')

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
