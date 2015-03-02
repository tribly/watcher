#!/usr/bin/python3

import sqlite3
import kat
import argparse
import webbrowser


class Watcher:
    def __init__(self):
        self.db_connection = sqlite3.connect('series.db')
        self.db = self.db_connection.cursor()

        self.parser = argparse.ArgumentParser()
        self.group = self.parser.add_mutually_exclusive_group(required=True)

    def fillArgsList(self):
        self.group.add_argument('-l', '--list',
                                 help='list all the series',
                                 action='count')
        self.group.add_argument('-n', '--next',
                                type=str)
        self.group.add_argument('-a', '--add',
                                type=str)
        self.group.add_argument('--edit',
                                 help='edit series. Must provide -s -e',
                                 type=str)

        self.parser.add_argument('-s', '--season',
                                 type=int)
        self.parser.add_argument('-e', '--episode',
                                 type=int)
        self.parser.add_argument('--last',
                                 type=int)

    def newSeason(self, name):
        self.incrementSeason(name)

        self.db.execute("UPDATE series\
                         SET episode = 0\
                         WHERE name = ?",
                         (name,))

    def addSeries(self, name, season, episode, last_episode):
        self.db.execute('INSERT INTO series\
                          (name, season, episode, last_episode)\
                          VALUES (?, ?, ?, ?)',
                          (name, season, episode, last_episode))

        self.db_connection.commit()
    def incrementEpisode(self, name):
        self.db.execute("SELECT last_episode\
                         FROM series\
                         WHERE name = ?",
                                       (name,))
        last_episode = self.db.fetchone()

        self.db.execute("SELECT episode\
                         FROM series\
                         WHERE name = ?",
                                          (name,))
        current_episode = self.db.fetchone()

        if current_episode == last_episode:
            self.newSeason(name)

        self.db.execute("UPDATE series\
                         SET episode = episode + 1\
                         WHERE name = ?",
                        (name,))

        self.db_connection.commit()

    def incrementSeason(self, name):
        self.db.execute("UPDATE series\
                         SET season = season + 1\
                         WHERE name = ?",
                        (name,))
        self.db_connection.commit()

    def editSeries(self, name, season, episode):
        self.db.execute('UPDATE series\
                         SET season = ?,\
                             episode = ?\
                         WHERE name = ?',
                         (season, episode, name))
        self.db_connection.commit()

    def listSeries(self, more=False):
        if not more:
            self.db.execute("SELECT name\
                             FROM series")
        else:
            self.db.execute("SELECT name, season, episode\
                             FROM series")

        infos = self.db.fetchall()

        for series in infos:
            print(series[0])
            if more:
                print('  season:', series[1])
                print('  episode:', series[2])

    def openSite(self, data):
        new = 2
        base_url = 'http://kickass.to/usearch/'
        order = '/?field=size&order=desc'

        name = data[0].replace(' ', '%20') + ' '
        season = data[1]
        episode = data[2]

        if season < 10:
            season = 's0' + str(season)
        else:
            season = 's' + str(season)

        if episode < 10:
            episode = 'e0' + str(episode)
        else:
            episode = 'e' + str(episode)

        url = base_url + name + season + episode + order

        webbrowser.get('chromium').open(url, new=new)

    def getSeriesData(self, name):
        self.db.execute('SELECT name, season, episode\
                         FROM series\
                         WHERE name = ?',
                         (name,))

        info = self.db.fetchall()
        data = []

        for stuff in info[0]:
            data.append(stuff)
        print(data)
        return data

    def main(self):
        self.fillArgsList()
        args = self.parser.parse_args()

        if args.list == 1:
            self.listSeries()
        elif args.list == 2:
            self.listSeries(True)

        if args.next:
            data = self.getSeriesData(args.next)
            if data:
                self.openSite(data)
                self.incrementEpisode(args.next)
            else:
                print('No series found')

        if args.add:
            name         = args.add
            season       = args.season
            episode      = args.episode
            last_episode = args.last

            self.addSeries(name, season, episode, last_episode)

        if args.edit:
            name         = args.edit
            season       = args.season
            episode      = args.episode

            self.editSeries(name, season, episode)

if __name__ == '__main__':
    s = Watcher()
    s.main()
