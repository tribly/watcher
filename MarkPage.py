#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk

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

        self.controller.frames[StartPage.StartPage].fillNextList()
        self.controller.showFrame(StartPage.StartPage)

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
