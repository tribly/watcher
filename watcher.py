#!/usr/bin/env python
import sqlite3
import os

class SomeClass:
    def __init__(self):
        self.db_connection = self.connect()


    def connect(self):
        con = sqlite3.connect('/home/heinz/downloads/testdb')

        return con


    def menu(self):
        while True:
            print("-----------")
            print("[1]: Next episode")
            print("[2]: Add series")
            print("[3]: List series")
            print("[4]: Delete series")
            print("[0]: Exit")
            print("---------------")
            decision = int(input("Option: "))

            if decision == 0:
                break

            if decision == 1:
                self.listDB()

                option_series = input("Option: ")

                self.openSite(option_series)
            elif decision == 2:
                print("----------")
                name    = input("Enter name: ")
                season  = input("Enter season: ")
                episode = input("Enter episode: ")

                data = [name, season, episode]

                self.addSeries(data)
            elif decision == 3:
                self.listDB()
            elif decision == 4:
                self.listDB()

                option_series = input("Option: ")

                self.deleteSeries(option_series)

        self.db_connection.close()


    def deleteSeries(self, id_):
        cur = self.db_connection.cursor()

        cur.execute("DELETE FROM series WHERE id = ?", id_)
        self.db_connection.commit()

        print("Deleted", id_)


    def listDB(self):
        cur = self.db_connection.cursor()

        cur.execute("select name from series")

        names = cur.fetchall()

        number = 1

        print("-----------")
        for name in names:
            print("[" + str(number) + "]", name[0])
            number = number + 1


    def concData(self, data_):
        name = str(data_[0])
        season = int(data_[1])
        episode = int(data_[2])

        name = name.replace(" ", "%20")

        if season < 10:
            season = "0" + str(season)

        if episode < 10:
            episode = "0" + str(episode)

        return (name, season, episode)


    def incrementEpisode(self, name_):
        cur = self.db_connection.cursor()
        cur.execute("update series set episode = episode + 1 where name=\"" + name_ + "\"")
        self.db_connection.commit()


    def decrementEpisode(self, name_):
        cur = self.db_connection.cursor()
        cur.execute("update series set episode = episode - 1 where name=\"" + name_ + "\"")
        self.db_connection.commit()


    def incrementSeason(self, name_):
        cur = self.db_connection.cursor()
        cur.execute('update series set season = season + 1 where name = "' + name_ + '"')
        cur.execute('update series set episode = 1 where name = "' + name_ + '"')
        self.db_connection.commit()


    def decrementSeason(self, name_):
        cur = self.db_connection.cursor()
        cur.execute('update series set season = season - 1 where name = "' + name_ + '"')
        self.db_connection.commit()


    def openSite(self, id_):
        cur = self.db_connection.cursor()

        cur.execute("select name,season,episode from series where id=?", id_)
        series = cur.fetchone()
        names = concData(series)

        url = "https://kickass.so/usearch/" + \
                names[0] + "%20s" + str(names[1]) + "e" + str(names[2]) + "?field=seeders&sorder=desc"

        os.system('chromium ' + url)
        self.incrementEpisode(series[0])


    def addSeries(self, data_):
        cur = self.db_connection.cursor()
        sql = "insert into series (name, season, episode) values (\"" + \
                data_[0] + "\"," + data_[1] + "," + data_[2] + ")"

        cur.execute(sql)
        self.db_connection.commit()

        print("Added", data_[0], "s:", data_[1], "e:", data_[2])


if __name__ == '__main__':
    s = SomeClass()
    s.menu()
