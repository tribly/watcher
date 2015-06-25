#!/usr/bin/env python
# encoding: utf-8

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
import webbrowser

class AboutPage(ttk.Frame):
    """Display info about the app"""

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        self.link1 = 'http://www.flaticon.com/authors/freepik'
        self.link2 = 'http://www.flaticon.com/'
        self.link3 = 'http://thetvdb.com/'

        self.label1 = tk.Label(self, text = 'Developer:')
        self.label2 = tk.Label(self, text = 'Hrvoje Hodak', fg = "#0000FF", cursor = 'hand2')
        self.label3 = tk.Label(self, text = 'Powered by:')
        self.label4 = tk.Label(self, text = 'http://thetvdb.com/', fg = "#0000FF", cursor = 'hand2')
        self.label5 = tk.Label(self, text = 'Menu icon by:')
        self.label6 = tk.Label(self, text = 'Freepik', fg = "#0000FF", cursor = 'hand2')

        self.label1.pack(anchor = "w")
        self.label2.pack(anchor = "w", ipadx = '25', pady = '0 10')
        self.label3.pack(anchor = "w")
        self.label4.pack(anchor = "w", ipadx = '25', pady = '0 10')
        self.label5.pack(anchor = "w")
        self.label6.pack(anchor = "w", ipadx = '25', pady = '0 10')

        self.font = font.Font(self.label2, self.label1.cget("font"))
        self.font.configure(underline = True)
        self.label2.configure(font = self.font)
        self.label4.configure(font = self.font)
        self.label6.configure(font = self.font)

        self.label2.bind('<Button-1>', self.openDev)
        self.label4.bind('<Button-1>', self.openDB)
        self.label6.bind('<Button-1>', self.openIcon)

    def openDev(self, event):
        webbrowser.open('https://tribly.de/')

    def openDB(self, event):
        webbrowser.open(self.link3)

    def openIcon(self, event):
        webbrowser.open(self.link1)

    def setTakeFocus(self):
        pass

    def unsetTakeFocus(self):
        pass


