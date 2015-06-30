#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk

class EditPage(tk.Frame):
    """Page for editing series, like deleting"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.bg_color = self.controller['bg']

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)

        self.label = ttk.Label(self, takefocus = False)
        self.label.config(text = 'Select series to edit')
        self.label.grid(row = 0, column = 0, pady = "10")

        self.listbox = tk.Listbox(self, takefocus = False)
        self.listbox.config(highlightcolor = self.bg_color)
        self.listbox.bind('<Double-Button-1>', controller.getSelectionEdit)
        self.listbox.bind('<Return>', controller.getSelectionEdit)
        self.listbox.grid(row = 1, column = 0, sticky = "news")

        self.populateListbox()

    def populateListbox(self):
        """Insert alle the series names into the box

        """
        names = self.controller.getSeriesNames()

        for name in names:
            self.listbox.insert(tk.END, name)

    def setTakeFocus(self):
        """Let the Listox-widget get the focus by tabbing

        """
        self.listbox.config(takefocus = True)
        self.listbox.focus_set()

    def unsetTakeFocus(self):
        """Don't let the Listbox widget get any focus by tabbing

        """
        self.listbox.config(takefocus=False)


