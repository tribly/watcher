#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk

class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.listbox = tk.Listbox(self, takefocus=False, width = 30)
        self.listbox.bind('<Return>', controller.getSelectionSearch)
        self.listbox.bind('<Double-Button-1>', controller.getSelectionSearch)
        self.listbox.grid()

        self.config(takefocus=False)

    def setTakeFocus(self):
        self.listbox.config(takefocus=True)
        self.listbox.focus_set()

    def unsetTakeFocus(self):
        self.listbox.config(takefocus=False)

    def fillListbox(self, array):
        for name in array:
            self.listbox.insert(tk.END, name)

