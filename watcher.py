#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import SeriesItem
import SeriesInfo
import XMLParser
import Database

class Watcher(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.fetcher = SeriesInfo.SeriesInfo()
        self.xml = XMLParser.XMLParser()
        self.db = Database.Database()

        self.container = tk.Frame(self)
        self.container.pack(side = "top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.bind('<Control-q>', self.closeApp)

        self.frames = {}

        for F in (StartPage, SearchPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def fillSearchList(self, array):
        self.frames[SearchPage].fillListbox(array)
        self.frames[SearchPage].tkraise()

    def getSelectionSearch(self, event):
        entry = self.frames[SearchPage].listbox.curselection()
        selection = self.frames[SearchPage].listbox.get(entry)

        self.frames[StartPage].addSeries2(selection)

        self.show_frame(StartPage)

    def show_frame(self, c):
        frame = self.frames[c]
        frame.tkraise()

    def closeApp(self, event):
        self.db.closeDB()
        self.destroy()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.listbox = tk.Listbox(self, height = 5)
        self.listbox.bind('<Return>', self.getSelection)

        self.addSeriesBox = tk.Entry(self)
        self.addSeriesBox.bind('<Return>', self.addSeries)

        self.fillNextList()

        self.addSeriesBox.grid()
        self.listbox.grid()

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
        selection = self.listbox.get(entry[0])

        return selection

    def addSeries(self, event):
        name = self.addSeriesBox.get()
        info = self.controller.fetcher.searchSeries(name)
        self.search_dict = self.controller.xml.searchSeries(info)

        if len(self.search_dict) > 1:
            names = []
            for k in self.search_dict:
                names.append(k)

            self.controller.fillSearchList(names)
        else:
            for k in self.search_dict.keys():
                self.addSeries2(k)

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
        self.listbox.grid()

    def fillListbox(self, array):
        for name in array:
            self.listbox.insert(tk.END, name)

    def getSelection(self):
        entry = self.listbox.curselection()
        selection = self.listbox.get(entry[0])

        return selection


if __name__ == "__main__":
    app = Watcher()
    app.mainloop()
