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

        self.status_bar = ttk.Label(self)
        self.status_bar.pack()

        self.bind('<Control-q>', self.closeApp)

        self.frames = {}

        for F in (StartPage, SearchPage, WatchPage, MarkPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(MarkPage)

    def updateStatus(self, text):
        self.status_bar.config(text=text)
        self.status_bar.update_idletasks()

    def clearStatus(self):
        self.status_bar.config(text='')
        self.status_bar.update_idletasks()

    def fillSearchList(self, array):
        self.frames[SearchPage].fillListbox(array)
        self.showFrame(SearchPage)

    def getSelectionSearch(self, event):
        entry = self.frames[SearchPage].listbox.curselection()
        selection = self.frames[SearchPage].listbox.get(entry)

        self.frames[StartPage].addSeries2(selection)

        self.showFrame(StartPage)

    def getSelectionWatch(self, event):
        entry = self.frames[WatchPage].listbox.curselection()
        selection = self.frames[WatchPage].listbox.get(entry)

        if selection == 'kat':
            self.prepareKATLink(self.start_page_selection)
        elif selection == 'watchseries':
            self.prepareWSLink(self.start_page_selection)
        elif selection == 'only next':
            # TODO: placeholder
            pass
        elif selection == 'mark list':
            pass

        self.setWatched(self.start_page_selection)
        self.frames[StartPage].fillNextList()

        self.showFrame(StartPage)

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

        self.start_page_selection = selection

        self.frames[WatchPage].setLabel(self.start_page_selection)
        self.showFrame(WatchPage)

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


class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.listbox = tk.Listbox(self, height = 10)
        self.listbox.bind('<Return>', self.controller.getSelectionStart)
        self.listbox.bind('<Double-Button-1>', self.controller.getSelectionStart)

        self.addSeriesBox = ttk.Entry(self)
        self.addSeriesBox.insert(tk.END, "Add series...")
        self.addSeriesBox.bind('<Return>', self.addSeries)
        self.addSeriesBox.bind('<Double-Button-1>', self.addSeries)

        self.fillNextList()

        self.addSeriesBox.grid(pady = "10")
        self.listbox.grid()
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
                self.controller.updateStatus('fetching info for: ' + k)
                self.addSeries2(k)
                self.controller.updateStatus('added: ' + k)

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

    def setTakeFocus(self):
        self.addSeriesBox.config(takefocus=True)
        self.listbox.config(takefocus=True)
        self.listbox.focus_set()

    def unsetTakeFocus(self):
        self.listbox.config(takefocus=False)
        self.addSeriesBox.config(takefocus=False)


class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.config(takefocus=False)

        self.listbox = tk.Listbox(self, takefocus=False)
        self.listbox.bind('<Return>', controller.getSelectionSearch)
        self.listbox.bind('<Double-Button-1>', controller.getSelectionSearch)

        self.listbox.grid()

    def setTakeFocus(self):
        self.listbox.config(takefocus=True)
        self.listbox.focus_set()

    def unsetTakeFocus(self):
        self.listbox.config(takefocus=False)

    def fillListbox(self, array):
        for name in array:
            self.listbox.insert(tk.END, name)

class WatchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.label = ttk.Label(self, takefocus=False)

        self.listbox = tk.Listbox(self, takefocus=False)
        self.listbox.insert(tk.END, 'kat')
        self.listbox.insert(tk.END, 'watchseries')
        self.listbox.insert(tk.END, 'only next')
        self.listbox.insert(tk.END, 'mark list')
        self.listbox.bind('<Return>', controller.getSelectionWatch)
        self.listbox.bind('<Double-Button-1>', controller.getSelectionWatch)

        self.label.grid(pady = "10")
        self.listbox.grid()

    def setLabel(self, text):
        self.label.config(text = text)

    def setTakeFocus(self):
        self.listbox.config(takefocus=True)
        self.listbox.focus_set()

    def unsetTakeFocus(self):
        self.listbox.config(takefocus=False)

class MarkPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # TODO move to Watcher
        self.controller = controller

        self.var_list = []

        #self.var_list.append(tk.IntVar())
        #self.var_list.append(tk.IntVar())

        self.label = ttk.Label(self, takefocus=False)
        self.button = ttk.Button(self, takefocus=False, command = self.actio)

        ####
        self.label.config(text = 'hihohahihohahihoha')
        self.button.config(text = 'lala')
        ###
        #self.cb = ttk.Checkbutton(self)
        #self.cb.config(text = 'testbutton', variable = self.var_list[0])
        #self.cb2 = ttk.Checkbutton(self)
        #self.cb2.config(text = 'testbutton', variable = self.var_list[1])

        self.label.grid(pady = "10", padx = 10, row = 0, column = 0, sticky = "w")
        self.button.grid(row = 0, column = 1, sticky = "w")
        #self.cb.grid(row = 2, column = 0, sticky = "w")
        #self.cb2.grid(row = 3, column = 0, padx = (35,0), sticky = "w")

    def populateMenu(self):
        row = 1
        season_count = 1
        episode_count = 1
        for season in self.var_list:
            for episode in season:
                cb = ttk.Checkbutton(self, variable = episode, text = episode_count)
                cb.grid(row = row, column = 0)
                episode_count += 1
                row += 1
            break
            episode_count = 0
            season_count += 1

    def fillVarList(self, data):
        for season in data.keys():
            self.var_list.append([])
            for n in range(data[season]):
                self.var_list[season - 1].append(tk.IntVar())


    # TODO: refactor
    def actio(self):
        data = self.controller.db.getSeasonEpisodeData('Family Guy -')
        self.fillVarList(data)
        self.populateMenu()

    def setLabel(self, text):
        self.label.config(text = text)

    def setTakeFocus(self):
        pass
        #self.listbox.config(takefocus=True)
        #self.listbox.focus_set()

    def unsetTakeFocus(self):
        pass
        #self.listbox.config(takefocus=False)

if __name__ == "__main__":
    app = Watcher()
    app.mainloop()
