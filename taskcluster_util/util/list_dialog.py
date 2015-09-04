#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from Tkinter import *
import ttk

import textwrap
import easygui


def runTest(*args):
    idxs = lbox.curselection()
    #lbox.see(idxs)
    print('Select: {}'.format(idxs))

    title = 'Load Options Error'
    msg = textwrap.dedent('''\
    Can not load Credentials from user input.
    Run with no credentials.

    * Tips: [Enter] OK
    ''')
    easygui.msgbox(msg, title)


root = Tk()
root.title('Askeing Testing GUI')

input_list = ('OOXX', 'X', 'y', 'z', 'a', 'b', 'c', 'ASK', 'Moz', 'Taipei', 'Mozilla', 'Test')

input_list_var = StringVar(value=input_list)


c = ttk.Frame(root, padding=(5, 5, 12, 0))
c.grid(column=0, row=0, sticky=(N, W, E, S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# create widgets
lbl = ttk.Label(c, text='This is test window.')
lbox = Listbox(c, listvariable=input_list_var, height=20, width=50, selectmode=EXTENDED)
send = ttk.Button(c, text='Test', command=runTest, default='active')

# grid widgets
lbl.grid(column=0, row=0, sticky=E)
send.grid(column=1, row=0, sticky=E)
lbox.grid(column=0, row=1, columnspan=2, sticky=(N, S, E, W))
c.grid_columnconfigure(2, weight=1)
c.grid_rowconfigure(2, weight=1)

# set event bindings
lbox.bind('<Double-1>', runTest)

# colorize listbox
for i in range(0, len(input_list), 2):
    lbox.itemconfigure(i, background='#f0f0ff')

lbox.select_set(0)

root.mainloop()
