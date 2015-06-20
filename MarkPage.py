#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk
from StartPage import StartPage

class MarkPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.scrollbar = tk.Scrollbar(self)
        self.textbox = tk.Text(self, yscrollcommand = self.scrollbar.set)

        # TODO move to Watcher
        self.controller = controller

        self.var_list = []
        self.mark_season = []
        self.cb_ep_list = []

        self.label = ttk.Label(self, takefocus=False)
        self.button = ttk.Button(self, takefocus=False, command = self.testfun)

        self.scrollbar.config(command = self.textbox.yview)

        ####
        self.label.config(text = '')
        self.button.config(text = 'Done')
        ###

        self.label.grid(pady = "10", padx = 10, row = 0, column = 0, sticky = "w")
        self.button.grid(row = 0, column = 1, sticky = "w")
        self.textbox.grid(row = 1, columnspan = 2, sticky="NS")
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

    def clearVars(self):
        self.var_list = []
        self.mark_season = []

    def startSelection(self):
        self.clearBoxes()
        self.clearVars()
        name = self.label["text"]
        data = self.controller.db.getSeasonEpisodeData(name)
        self.fillVarList(data)
        self.textbox.config(state = tk.NORMAL)
        self.populateMenu()
        self.textbox.config(state = tk.DISABLED)

    def markSeason(self):
        season_nr = 1
        for season in self.mark_season:
            state = season.get()

            for episode in self.var_list[season_nr - 1]:
                if state == 1:
                    episode.set(1)
                else:
                    episode.set(0)

            for cb in self.cb_ep_list[season_nr - 1]:
                if state == 1:
                    cb.config(state = tk.ACTIVE)
                else:
                    cb.config(state = tk.NORMAL)

            season_nr += 1

    def seasonWatched(self, nr):
        for episode in self.var_list[nr - 1]:
            if episode.get() == 0:
                print(False)
                return False

        return True

    def populateMenu(self):
        season_count = 1
        episode_count = 1
        cb_season = []

        for season in self.var_list:
            self.mark_season.append(tk.IntVar())
            cb = ttk.Checkbutton(self, variable = self.mark_season[season_count - 1],
                                 text = "Season " + str(season_count),
                                 command = self.markSeason)

            self.textbox.window_create(tk.END, window = cb)

            if self.seasonWatched(season_count):
                self.mark_season[season_count - 1].set(1)
                cb.config(state = tk.ACTIVE)

            for episode in season:
                cb = ttk.Checkbutton(self, variable = episode,
                                     text = "Episode " + str(episode_count))
                cb_season.append(cb)
                if episode == 1:
                    cb.config(state = tk.ACTIVE)
                self.textbox.insert(tk.END, "\n  ")
                self.textbox.window_create(tk.END, window = cb)
                episode_count += 1

            self.cb_ep_list.append(cb_season)
            cb_season = []
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
