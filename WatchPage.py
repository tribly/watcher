#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk

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

