#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk

class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.listbox = tk.Listbox(self, height = 10, width = 30)
        self.listbox.bind('<Return>', self.controller.getSelectionStart)
        self.listbox.bind('<Double-Button-1>', self.controller.getSelectionStart)

        self.addSeriesBox = ttk.Entry(self)
        self.addSeriesBox.insert(tk.END, "Add series...")
        self.addSeriesBox.bind('<Return>', self.addSeries)

        self.addSeriesBox.grid(pady = "10")
        self.listbox.grid()
        self.listbox.focus_set()

        self.fillNextList()

        self.search_dict = {}

    def fillNextList(self):
        self.listbox.delete(0, tk.END)
        series_ids = self.controller.db.getUniqueIDs()

        series_next = []

        for id in series_ids:
            series_next.append(self.controller.db.getNext(id[0]))

        series_next = self.controller.checkDates(series_next)

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

        self.controller.updateStatus('searching...')

        info = self.controller.fetcher.searchSeries(name)
        self.search_dict = self.controller.xml.searchSeries(info)

        self.controller.clearStatus()

        if len(self.search_dict) > 1:
            names = []
            for k in self.search_dict:
                names.append(k)

            self.controller.fillSearchList(names)
        else:
            for k in self.search_dict.keys():
                self.addSeries2(k)

    def addSeries2(self, name):
        if not self.controller.checkIfExists(name):
            self.controller.updateStatus('Already in database')
            return False

        selected_series_id = self.search_dict[name]

        # html
        self.controller.updateStatus('fetching info for: ' + name)
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
        self.controller.updateStatus('added: ' + name)
        return True

    def getSeriesInfo(self, id):
        return self.controller.fetcher.getSeriesInfo(id)

    def setTakeFocus(self):
        self.addSeriesBox.config(takefocus=True)
        self.listbox.config(takefocus=True)
        self.listbox.focus_set()

    def unsetTakeFocus(self):
        self.listbox.config(takefocus=False)
        self.addSeriesBox.config(takefocus=False)
