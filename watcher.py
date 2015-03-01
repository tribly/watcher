import sqlite3
import kat
import sys

class Watcher:
    def __init__(self):
        self.db_connection = sqlite3.connect('series.db')
        self.db = self.db_connection.cursor()

    def newSeason(self, name):
        self.incrementSeason(name)

        self.db.execute("UPDATE series\
                         SET episode = 0\
                         WHERE name = ?",
                         (name,))

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

if __name__ == '__main__':
    s = Watcher()
    s.incrementEpisode('test')
