#!/usr/bin/env python
# encoding: utf-8

import tkinter
import SeriesItem
import SeriesInfo
import XMLParser
import Database

class gui_main():

    def __init__(self):
        self.fetcher = SeriesInfo.SeriesInfo()
        self.xml = XMLParser.XMLParser()
        self.db = Database.Database()

        self.main_win = tkinter.Tk()
        self.main_win.bind('q', self.closeApp)

        self.listbox = tkinter.Listbox(self.main_win, height = 5)
        self.listbox.bind('<Return>', self.getSelection)

        self.addSeriesBox = tkinter.Entry(self.main_win)
        self.addSeriesBox.bind('<Return>', self.addSeries)

        self.fillNextList()
        self.addSeriesBox.grid(row = 0, column = 0)
        self.listbox.grid(row = 1, column = 0)

        self.main_win.mainloop()

    def fillNextList(self):
        series_ids = self.db.getUniqueIDs()

        series_next = []

        for id in series_ids:
            series_next.append(self.db.getNext(id[0]))

        pretty_info = self.compactInfo(series_next)

        for series in pretty_info:
            self.listbox.insert(tkinter.END, series)

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

    def closeApp(self, event):
        self.db.closeDB()
        self.main_win.destroy()

    def addSeries(self, event):
        name = self.addSeriesBox.get()
        info = self.fetcher.searchSeries(name)
        many_series = self.xml.searchSeries(info)
        # TODO: implement selection for multiple results
        if len(many_series) > 1:
            print('multiple results, not implemented yet')
            return

        complete_info = self.getSeriesInfo(many_series[0][1])
        compact_info = self.xml.getSeriesInfo(complete_info)

        db_info = []

        for element in compact_info:
            a = []
            a.append(many_series[0][0])
            a.append(many_series[0][1])
            for i in element:
                a.append(i)

            db_info.append(a)

        self.db.writeData(db_info)

    def getSeriesInfo(self, id):
        return self.fetcher.getSeriesInfo(id)


if __name__ == "__main__":
    gui_main()
