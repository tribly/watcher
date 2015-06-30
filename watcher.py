#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk
import SeriesItem
import SeriesInfo
import XMLParser
import Database
import webbrowser
import datetime
from MarkPage import MarkPage
from SearchPage import SearchPage
from StartPage import StartPage
from WatchPage import WatchPage
from UpdateSeries import UpdateSeries
from AboutPage import AboutPage
from EditPage import EditPage

class Watcher(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.fetcher = SeriesInfo.SeriesInfo()
        self.xml = XMLParser.XMLParser()
        self.db = Database.Database()
        self.updater = UpdateSeries(self)
        self.today = datetime.date.today()

        self.series_selection = ""

        self.container = ttk.Frame(self, padding = "5 5 5 5")
        self.container.pack(side = "top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.status_bar = ttk.Label(self)
        self.status_bar.pack()

        self.bind('<Control-q>', self.closeApp)

        self.frames = {}

        for F in (StartPage, SearchPage,
                  WatchPage, MarkPage,
                  AboutPage, EditPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame('StartPage')
        self.fetchUpdates()

    def fetchUpdates(self):
        """Fetch the newest updates for series
        @return: @todo

        """
        self.updater.start()

    def checkIfExists(self, name):
        if self.db.getIdFromName(name) == None:
            return True
        else:
            return False

    def updateStatus(self, text):
        self.status_bar.config(text=text)
        self.status_bar.update_idletasks()

    def clearStatus(self):
        self.status_bar.config(text='')
        self.status_bar.update_idletasks()

    def fillSearchList(self, array):
        self.frames[SearchPage].fillListbox(array)
        self.showFrame('SearchPage')

    def getSelectionEdit(self, event):
        """Get the selected item from the widget

        @param event @todo
        @return: @todo

        """
        entry = self.frames[EditPage].listbox.curselection()
        selection = self.frames[EditPage].listbox.get(entry)

        self.frames[WatchPage].setLabel(selection)
        self.showFrame('WatchPage')

    def getSelectionSearch(self, event):
        entry = self.frames[SearchPage].listbox.curselection()
        selection = self.frames[SearchPage].listbox.get(entry)

        self.frames[StartPage].addSeries2(selection)

        self.showFrame('StartPage')

    def getSelectionWatch(self, event):
        try:
            entry = self.frames[WatchPage].listbox.curselection()
            selection = self.frames[WatchPage].listbox.get(entry)
        except tk.TclError as e:
            pass
        try:
            entry = self.frames[WatchPage].listbox_options.curselection()
            selection = self.frames[WatchPage].listbox_options.get(entry)
        except tk.TclError as e:
            pass

        if selection == 'kat':
            self.prepareKATLink(self.series_selection)
            #self.setWatched(self.series_selection)
            self.frames[StartPage].fillNextList()

            self.showFrame('StartPage')
        elif selection == 'watchseries':
            self.setWatched(self.series_selection)
            self.frames[StartPage].fillNextList()

            self.showFrame('StartPage')
            self.prepareWSLink(self.series_selection)
        elif selection == 'Set watched':
            self.setWatched(self.series_selection)
            self.frames[StartPage].fillNextList()

            self.showFrame('StartPage')
            # TODO: placeholder
            pass
        elif selection == 'Mark seasons':
            pos = self.series_selection.find('-')
            name = self.series_selection[:pos - 1]
            self.frames[MarkPage].setName(name)
            self.frames[MarkPage].startSelection()
            self.showFrame('MarkPage')

        elif selection == 'Delete series':
            pos = self.series_selection.find('-')
            name = self.series_selection[:pos - 1]
            series_id = self.db.getIdFromName(name)
            self.db.deleteSeries(series_id)
            self.updateStatus('Deleted ' + name)
            self.frames[StartPage].fillNextList()
            self.showFrame('StartPage')


    def setWatched(self, name):
        self.db.setWatched(name)

    def prepareWSLink(self, info):
        info = info.replace(' - ', ' ')
        info = info.replace(' ', '_')
        info = info.replace('!', '')
        info_tmp = info[:-6]

        season = int(info[-5:-3])
        episode = int(info[-2:])

        info_tmp = info_tmp + 's' + str(season)
        info_tmp = info_tmp + '_e' + str(episode)

        url_prefix = 'http://watchseries.lt/episode/'
        url_suffix = '.html'

        url = url_prefix + info_tmp + url_suffix

        webbrowser.open(url)

    def prepareKATLink(self, info):
        info = info.replace(' - ', ' ')
        info = info.replace(' ', '%20')

        url_prefix = 'https://kat.cr/usearch/'
        url_suffix = '/?field=size&sorder=desc'

        url = url_prefix + info + url_suffix

        webbrowser.open(url)

    def getSelectionStart(self, event):
        entry = self.frames[StartPage].listbox.curselection()
        selection = self.frames[StartPage].listbox.get(entry)

        self.series_selection = selection

        self.frames[WatchPage].setLabel(self.series_selection)
        self.showFrame('WatchPage')

    def getSeriesNames(self):
        """Get all the unique series names
        @return: list - All distinct series names

        """
        names = self.db.getDistinctNames()

        return names

    def showFrame(self, to_show):
        frames = {'StartPage' : StartPage,
                  'SearchPage' : SearchPage,
                  'WatchPage' : WatchPage,
                  'MarkPage' : MarkPage,
                  'AboutPage' : AboutPage,
                  'EditPage' : EditPage}

        frame = self.frames[frames[to_show]]
        frame.tkraise()
        frame.setTakeFocus()

        for f in self.frames:
            if f == to_show:
                continue
            self.frames[f].unsetTakeFocus()

    def closeApp(self, event):
        self.db.closeDB()
        self.destroy()

    def checkDates(self, data):
        next_list = []

        for series in data:
            date = series[4]

            #TODO: implement updates for single episodes
            # this is just a temporary fix
            if date == 'None':
                date = '2015-08-08'
            ###

            air_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            air_date = air_date.date()

            american_today = self.today - datetime.timedelta(1)

            if american_today >= air_date:
                next_list.append(series)

        return next_list

    def checkUpcoming(self, data):
        upcoming_list = []

        for series in data:
            date = series[4]

            #TODO: implement updates for single episodes
            # this is just a temporary fix
            if date == 'None':
                date = '2015-08-08'
            ###

            air_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            air_date = air_date.date()

            american_today = self.today - datetime.timedelta(1)
            delta = self.calculateTimedelta(air_date)

            if delta >= 0:
                continue

            if delta == -1:
                days = ' day'
            else:
                days = ' days'

            date_tup = (' - in ' + str(abs(delta)) + days,)
            series = series + date_tup
            upcoming_list.append(series)

        return upcoming_list

    def calculateTimedelta(self, date):
        american_today = self.today - datetime.timedelta(1)

        delta = (american_today - date).days

        return delta


if __name__ == "__main__":
    app = Watcher()
    app.mainloop()
