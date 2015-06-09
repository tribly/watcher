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

        self.addSeriesBox = tkinter.Entry(self.main_win)
        self.addSeriesBox.bind('<Return>', self.addSeries)
        self.addSeriesBox.grid(row = 0, column = 0)

        #################
        item_list = []

        names = ["game of thrones", "person of interest",
                 "orphan black", "family guy", "american dad"]

        for i in range(5):
            item_list.append(SeriesItem.SeriesItem(names[i], i+1, i+2))

        for i in item_list:
            self.listbox.insert(tkinter.END, i.getInfo())
        ###################
        self.listbox.bind('<Return>', self.getSelection)
        self.listbox.grid()

        self.main_win.mainloop()

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
