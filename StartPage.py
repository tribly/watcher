#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk
from PIL import Image

class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)


        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.controller = controller
        self.menu_image = ImageTk.PhotoImage(Image.open('assets/menu_button.png'))

        self.bg_color = controller['bg']

        self.listbox = tk.Listbox(self, highlightcolor = self.bg_color)
        self.listbox.config(height = 10, width = 30, activestyle = 'none')
        self.listbox.bind('<Return>', self.controller.getSelectionStart)
        self.listbox.bind('<Double-Button-1>', self.controller.getSelectionStart)
        self.listbox.grid(row = 1, column = 0, columnspan = 2, sticky = "news")

        self.menu_button = tk.Menubutton(self)
        self.menu_button.config(image = self.menu_image)
        self.menu_button.config(relief = "raised")
        self.menu_button.grid(row = 0, column = 1, sticky = "E", pady = "5")

        self.listbox_upcoming = tk.Listbox(self, highlightcolor = self.bg_color)
        self.listbox_upcoming.config(height = 10, width = 30, activestyle = 'none')
        self.listbox_upcoming.bind('<Return>')
        self.listbox_upcoming.bind('<Double-Button-1>')
        self.listbox_upcoming.grid(row = 3, column = 0, columnspan = 2, sticky = "news")

        self.label_upcoming = tk.Label(self, text="Upcoming")
        self.label_upcoming.grid(row = 2, column = 0, sticky = "w",
                                 pady = (10,0), columnspan = 2)

        self.addSeriesBox = ttk.Entry(self)
        self.addSeriesBox.insert(tk.END, "Add series...")
        self.addSeriesBox.bind('<Return>', self.addSeries)
        self.addSeriesBox.grid(row = 0, column = 0,  sticky = "w")

        self.listbox.focus_set()

        self.populateMenuButton()
        self.fillNextList()
        self.fillUpcomingList()

        self.search_dict = {}

    def populateMenuButton(self):
        self.menu_button.menu = tk.Menu(self.menu_button, tearoff = False)
        self.menu_button["menu"] = self.menu_button.menu

        #TODO: implement
        self.menu_button.menu.add_command(command = self.openEditPage,
                                          label = "Edit series")
        self.menu_button.menu.add_separator()
        self.menu_button.menu.add_command(command = self.openAbout,
                                          label = "About")
        self.menu_button.menu.add_separator()
        self.menu_button.menu.add_command(command = self.closeApp,
                                          label = "Exit")

    def openEditPage(self):
        """Opens the edit Page
        @return: @todo

        """
        self.controller.showFrame('EditPage')

    def closeApp(self):
        """Closes the app

        """
        dummy_event = 0
        self.controller.closeApp(dummy_event)

    def openAbout(self):
        """@todo: Docstring for openAbout
        @return: @todo

        """
        self.controller.showFrame('AboutPage')

    def refreshUpcoming(self):
        """Reload the list after updating it
        :returns: @todo

        """
        self.listbox_upcoming.delete(0, tk.END)
        self.fillUpcomingList()

    def fillUpcomingList(self):
        """Populate the list of upcoming episodes
        @return: @todo

        """
        episode_ids = self.controller.db.getUpcoming()

        upcoming = []

        for episode_id in episode_ids:
            series = self.controller.db.getNextInfo(episode_id)
            upcoming.append(series)

        upcoming = self.controller.checkUpcoming(upcoming)
        pretty_info = self.compactInfo(upcoming, True)

        for series in pretty_info:
            self.listbox_upcoming.insert(tk.END, series)

    def fillNextList(self):
        self.listbox.delete(0, tk.END)
        series_ids = self.controller.db.getUniqueIDs()

        series_next = []

        for series_id in series_ids:
            series = self.controller.db.getNext(series_id)

            if series == None:
                continue
            else:
                series_next.append(series)

        series_next = self.controller.checkDates(series_next)

        pretty_info = self.compactInfo(series_next)

        for series in pretty_info:
            self.listbox.insert(tk.END, series)

    def compactInfo(self, data, upcoming = False):
        total_info = []

        for series in data:
            to_short = []
            to_short.append(series[0])
            to_short.append(series[2])
            to_short.append(series[3])

            if upcoming:
                to_short.append(series[5])

            info_string = self.concInfo(to_short, upcoming)
            total_info.append(info_string)

        return total_info

    def concInfo(self, data, upcoming = False):
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

        if upcoming:
            info_string += data[3]

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

