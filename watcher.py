#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk
import SeriesItem
import SeriesInfo
import XMLParser
import Database
import webbrowser

class Watcher(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.fetcher = SeriesInfo.SeriesInfo()
        self.xml = XMLParser.XMLParser()
        self.db = Database.Database()

        self.start_page_selection = ""

        self.container = ttk.Frame(self, padding = "5 5 5 5")
        self.container.pack(side = "top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.bind('<Control-q>', self.closeApp)

        self.frames = {}

        for F in (StartPage, SearchPage, WatchPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def updateStatus(self, widget, text):
        widget.config(text=text)
        widget.update_idletasks()

    def fillSearchList(self, array):
        self.frames[SearchPage].fillListbox(array)
        self.show_frame(SearchPage)

    def getSelectionSearch(self, event):
        entry = self.frames[SearchPage].listbox.curselection()
        selection = self.frames[SearchPage].listbox.get(entry)

        self.frames[StartPage].addSeries2(selection)

        self.show_frame(StartPage)

    def getSelectionWatch(self, event):
        entry = self.frames[WatchPage].listbox.curselection()
        selection = self.frames[WatchPage].listbox.get(entry)

        if selection == 'kat':
            self.prepareKATLink(self.start_page_selection)
        elif selection == 'watchseries':
            self.prepareWSLink(self.start_page_selection)
        elif selection == 'next':
            # TODO: implement just next
            pass

        self.show_frame(StartPage)

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

        self.start_page_selection = selection

        self.show_frame(WatchPage)

    def show_frame(self, c):
        frame = self.frames[c]
        frame.tkraise()
        frame.listbox.focus_set()

    def closeApp(self, event):
        self.db.closeDB()
        self.destroy()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.listbox = tk.Listbox(self, height = 10)
        self.listbox.bind('<Return>', self.controller.getSelectionStart)

        self.addSeriesBox = ttk.Entry(self)
        self.addSeriesBox.insert(tk.END, "Add series...")
        self.addSeriesBox.bind('<Return>', self.addSeries)

        self.status_bar = ttk.Label(self)

        self.fillNextList()

        self.addSeriesBox.grid(pady = "5")
        self.listbox.grid()
        self.status_bar.grid()
        self.listbox.focus_set()

        self.search_dict = {}

    def fillNextList(self):
        self.listbox.delete(0, tk.END)
        series_ids = self.controller.db.getUniqueIDs()

        series_next = []

        for id in series_ids:
            series_next.append(self.controller.db.getNext(id[0]))

        pretty_info = self.compactInfo(series_next)

        for series in pretty_info:
            self.listbox.insert(tk.END, series)

    def compactInfo(self, data):
        total_info = []

        for series in data:
            to_short = []
            to_short.append(series[0])
            to_short.append(series[2])
            to_short.append(series[3])

            info_string = self.concInfo(to_short)
            total_info.append(info_string)

        return total_info

    def concInfo(self, data):
        info_string = ""

        if data[1] < 10:
            data[1] = "0" + str(data[1])
        else:
            data[1] = str(data[1])

        if data[2] < 10:
            data[2] = "0" + str(data[2])
        else:
            data[2] = str(data[2])

        info_string += data[0] + ' - s' + data[1] + 'e' + data[2]

        return info_string

    def getSelection(self, event):
        entry = self.listbox.curselection()
        selection = self.listbox.get(entry)

        return selection

    def addSeries(self, event):
        name = self.addSeriesBox.get()

        self.controller.updateStatus(self.status_bar, 'searching...')

        info = self.controller.fetcher.searchSeries(name)
        self.search_dict = self.controller.xml.searchSeries(info)

        self.controller.updateStatus(self.status_bar, '')

        if len(self.search_dict) > 1:
            names = []
            for k in self.search_dict:
                names.append(k)

            self.controller.fillSearchList(names)
        else:
            for k in self.search_dict.keys():
                self.controller.updateStatus(self.status_bar, 'fetching info for: ' + k)
                self.addSeries2(k)
                self.controller.updateStatus(self.status_bar, 'added: ' + k)

    def addSeries2(self, name):
        selected_series_id = self.search_dict[name]

        # html
        complete_info = self.getSeriesInfo(selected_series_id)
        # xml
        compact_info = self.controller.xml.getSeriesInfo(complete_info)

        db_info = []

        for element in compact_info:
            a = []
            a.append(name)
            a.append(selected_series_id)

            for i in element:
                a.append(i)

            db_info.append(a)

        self.controller.db.writeData(db_info)
        self.fillNextList()

    def getSeriesInfo(self, id):
        return self.controller.fetcher.getSeriesInfo(id)


class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.listbox = tk.Listbox(self)
        self.listbox.bind('<Return>', controller.getSelectionSearch)

        self.status_bar = tk.Label(self)

        self.listbox.grid()
        self.status_bar.grid()

    def fillListbox(self, array):
        for name in array:
            self.listbox.insert(tk.END, name)

class WatchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.listbox = tk.Listbox(self)
        self.listbox.insert(tk.END, 'kat')
        self.listbox.insert(tk.END, 'watchseries')
        self.listbox.insert(tk.END, 'only next')
        self.listbox.bind('<Return>', controller.getSelectionWatch)

        self.status_bar = tk.Label(self)

        self.listbox.grid()
        self.status_bar.grid()


if __name__ == "__main__":
    app = Watcher()
    app.mainloop()
