#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk

class WatchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.bg_color = controller['bg']

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.label = ttk.Label(self, takefocus=False)
        self.label.grid(row = 0, column = 0, pady = "10")

        self.label_links = ttk.Label(self, takefocus = False)
        self.label_links.config(text = 'Links')
        self.label_links.grid(row = 1, column = 0,  sticky = 'w')

        self.listbox = tk.Listbox(self, takefocus=False)
        self.listbox.config(highlightcolor = self.bg_color)
        self.listbox.insert(tk.END, 'kat')
        self.listbox.insert(tk.END, 'watchseries')
        self.listbox.bind('<Return>', controller.getSelectionWatch)
        self.listbox.bind('<Double-Button-1>', controller.getSelectionWatch)
        self.listbox.grid(row = 2, column = 0, sticky = "news")

        self.label_options = ttk.Label(self, takefocus = False)
        self.label_options.config(text = 'Options')
        self.label_options.grid(row = 3, column = 0, pady = '10 0', sticky = 'w')

        self.listbox_options = tk.Listbox(self, takefocus=False)
        self.listbox_options.config(highlightcolor = self.bg_color)
        self.listbox_options.insert(tk.END, 'Set watched')
        self.listbox_options.insert(tk.END, 'Mark seasons')
        self.listbox_options.insert(tk.END, 'Delete series')
        self.listbox_options.bind('<Return>', controller.getSelectionWatch)
        self.listbox_options.bind('<Double-Button-1>', controller.getSelectionWatch)
        self.listbox_options.grid(row = 4, column = 0, sticky = "news")

    def setLabel(self, text):
        self.label.config(text = text)

    def setTakeFocus(self):
        self.listbox.config(takefocus=True)
        self.listbox.focus_set()

    def unsetTakeFocus(self):
        self.listbox.config(takefocus=False)

