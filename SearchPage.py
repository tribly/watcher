#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk

class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.bg_color = controller['bg']

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.label = tk.Label(self, highlightcolor = self.bg_color)
        self.label.config(text = "Search")
        self.label.grid(row = 0, column = 0, pady = 10, sticky = "n")

        self.listbox = tk.Listbox(self, takefocus=False, width = 30)
        self.listbox.config(highlightcolor = self.bg_color, activestyle = 'none')
        self.listbox.bind('<Return>', controller.getSelectionSearch)
        self.listbox.bind('<Double-Button-1>', controller.getSelectionSearch)
        self.listbox.grid(row = 1, column = 0, sticky = "news")

        self.config(takefocus=False)

    def setTakeFocus(self):
        self.listbox.config(takefocus=True)
        self.listbox.focus_set()

    def unsetTakeFocus(self):
        self.listbox.config(takefocus=False)

    def fillListbox(self, array):
        for name in array:
            self.listbox.insert(tk.END, name)

