#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk
import SeriesItem
import SeriesInfo
import MarkPage
import SearchPage
import StartPage
import WatchPage
import XMLParser
import Database
import webbrowser
import datetime

class Watcher(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.fetcher = SeriesInfo.SeriesInfo()
        self.xml = XMLParser.XMLParser()
        self.db = Database.Database()
        self.today = datetime.date.today()

        self.start_page_selection = ""

        self.container = ttk.Frame(self, padding = "5 5 5 5")
        self.container.pack(side = "top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.status_bar = ttk.Label(self)
        self.status_bar.pack()

        self.bind('<Control-q>', self.closeApp)

        self.frames = {}

        for F in (StartPage.StartPage,
                  SearchPage.SearchPage,
                  WatchPage.WatchPage,
                  MarkPage.MarkPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage.StartPage)

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
        self.frames[SearchPage.SearchPage].fillListbox(array)
        self.showFrame(SearchPage.SearchPage)

    def getSelectionSearch(self, event):
        entry = self.frames[SearchPage.SearchPage].listbox.curselection()
        selection = self.frames[SearchPage.SearchPage].listbox.get(entry)

        self.frames[StartPage.StartPage].addSeries2(selection)

        self.showFrame(StartPage.StartPage)

    def getSelectionWatch(self, event):
        entry = self.frames[WatchPage.WatchPage].listbox.curselection()
        selection = self.frames[WatchPage.WatchPage].listbox.get(entry)

        if selection == 'kat':
            self.prepareKATLink(self.start_page_selection)
            self.setWatched(self.start_page_selection)
            self.frames[StartPage.StartPage].fillNextList()

            self.showFrame(StartPage.StartPage)
        elif selection == 'watchseries':
            self.setWatched(self.start_page_selection)
            self.frames[StartPage.StartPage].fillNextList()

            self.showFrame(StartPage.StartPage)
            self.prepareWSLink(self.start_page_selection)
        elif selection == 'set watched':
            self.setWatched(self.start_page_selection)
            self.frames[StartPage.StartPage].fillNextList()

            self.showFrame(StartPage.StartPage)
            # TODO: placeholder
            pass
        elif selection == 'mark list':
            pos = self.start_page_selection.find('-')
            name = self.start_page_selection[:pos - 1]
            self.frames[MarkPage.MarkPage].setName(name)
            self.frames[MarkPage.MarkPage].startSelection()
            self.showFrame(MarkPage.MarkPage)


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
        entry = self.frames[StartPage.StartPage].listbox.curselection()
        selection = self.frames[StartPage.StartPage].listbox.get(entry)

        self.start_page_selection = selection

        self.frames[WatchPage.WatchPage].setLabel(self.start_page_selection)
        self.showFrame(WatchPage.WatchPage)

    def showFrame(self, to_show):
        frame = self.frames[to_show]
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
            air_date = datetime.datetime.strptime(series[4], "%Y-%m-%d")
            air_date = air_date.date()

            if self.today >= air_date:
                next_list.append(series)

        return next_list




if __name__ == "__main__":
    app = Watcher()
    app.mainloop()
