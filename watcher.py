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

        self.showFrame(StartPage)

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
            self.setWatched(self.start_page_selection)
            self.frames[StartPage].fillNextList()

            self.showFrame(StartPage)
        elif selection == 'watchseries':
            self.setWatched(self.start_page_selection)
            self.frames[StartPage].fillNextList()

            self.showFrame(StartPage)
            self.prepareWSLink(self.start_page_selection)
        elif selection == 'set watched':
            self.setWatched(self.start_page_selection)
            self.frames[StartPage].fillNextList()

            self.showFrame(StartPage)
            # TODO: placeholder
            pass
        elif selection == 'mark list':
            pos = self.start_page_selection.find('-')
            name = self.start_page_selection[:pos - 1]
            self.frames[MarkPage].setName(name)
            self.frames[MarkPage].startSelection()
            self.showFrame(MarkPage)


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

        self.listbox = tk.Listbox(self, height = 10, width = 30)
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

        self.listbox = tk.Listbox(self, takefocus=False, width = 30)
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

        self.listbox = tk.Listbox(self, takefocus=False, width = 30)
        self.listbox.insert(tk.END, 'kat')
        self.listbox.insert(tk.END, 'watchseries')
        self.listbox.insert(tk.END, 'set watched')
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
        self.scrollbar = tk.Scrollbar(self)
        self.textbox = tk.Text(self, yscrollcommand = self.scrollbar.set)

        # TODO move to Watcher
        self.controller = controller

        self.var_list = []

        self.label = ttk.Label(self, takefocus=False)
        self.button = ttk.Button(self, takefocus=False, command = self.testfun)

        self.scrollbar.config(command = self.textbox.yview)

        ####
        self.label.config(text = '')
        self.button.config(text = 'Done')
        ###

        self.label.grid(pady = "10", padx = 10, row = 0, column = 0, sticky = "w")
        self.button.grid(row = 0, column = 1, sticky = "w")
        self.textbox.grid(row = 1, sticky="NS")
        self.scrollbar.grid(row = 1, column = 2, sticky = "NS")

        self.textbox.config(width = 30, height = 10, bg = self["background"], bd = 0)
        self.textbox.config(state = tk.DISABLED)

    def setName(self, name):
        self.label.config(text=name)

    def testfun(self):
        data = []
        s = 0

        for season in self.var_list:
            data.append([])
            for episode in season:
                data[s].append(episode.get())
            s += 1

        self.controller.db.writeBulkData(self.label["text"], data)

        self.controller.frames[StartPage].fillNextList()
        self.controller.showFrame(StartPage)

    def clearBoxes(self):
        self.var_list = []
        self.textbox.config(state = tk.NORMAL)
        self.textbox.delete("1.0", tk.END)
        self.textbox.config(state = tk.DISABLED)

    def startSelection(self):
        self.clearBoxes()
        name = self.label["text"]
        data = self.controller.db.getSeasonEpisodeData(name)
        self.fillVarList(data)
        self.textbox.config(state = tk.NORMAL)
        self.populateMenu()
        self.textbox.config(state = tk.DISABLED)

    def populateMenu(self):
        season_count = 1
        episode_count = 1

        for season in self.var_list:
            self.textbox.insert(tk.END, "Season " + str(season_count))
            for episode in season:
                cb = ttk.Checkbutton(self, variable = episode,
                                     text = "Episode " + str(episode_count))
                if episode == 1:
                    cb.config(state = tk.ACTIVE)
                self.textbox.insert(tk.END, "\n")
                self.textbox.window_create(tk.END, window = cb)
                episode_count += 1

            self.textbox.insert(tk.END, "\n\n")
            episode_count = 1
            season_count += 1

    def fillVarList(self, data):
        season_index = 0
        for season in data:
            self.var_list.append([])
            for episode in season:
                val = tk.IntVar()
                val.set(episode)
                self.var_list[season_index].append(val)
            season_index += 1

    def setLabel(self, text):
        self.label.config(text = text)

    def setTakeFocus(self):
        self.textbox.config(takefocus=True)
        self.textbox.focus_set()

    def unsetTakeFocus(self):
        self.textbox.config(takefocus=False)

if __name__ == "__main__":
    app = Watcher()
    app.mainloop()
