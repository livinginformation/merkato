
#from exchange import Exchange
from merkato.merkato import Merkato

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.lines import Line2D

import datetime

import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox

import tkinter
import tkinter.ttk
import tkinter as tk
from tkinter import ttk

from operator import itemgetter
from collections import OrderedDict
import random
import time

from  bot import Bot
from app import App

LARGE_FONT= ("Liberation Mono", 12)
print(style.available)
style.use("dark_background")

"""
expected bot data format from merkato

{
"open_orders" : { "buy" : [(0.022, 0.5), 
                           (0.018, 1.5) ],
                  "sell"  : [(0.027, 0.5), 
                             (0.033,1.5) ]},
"filled_orders" :  {"buy" : [(0.022, 0.5, 2016-08-26 18:53:38), 
                             (0.018, 1.5, 2016-08-26 18:53:38) ],
                    "sell"  : [(0.027, 0.5 ,2016-08-26 18:53:38), 
                              (0.033,1.5, YYYY-MM-DD HH:MM:SS) ]},                          
"balances" : {"BTC" : 0.5121,
              "XMR": 15.2039},
"market" : (00.24,0.026),
"price"  : 0.025
                    
}
"""

if __name__ == "__main__":
    root = tk.Tk()

    def _scrollwheel(event):
        ''' TODO Function Description
        '''
        print("caught scroll", event.widget)
        return 'break'

    root.title("merkato (pre-release)")
    mystyle = ttk.Style()
    mystyle.theme_use('clam')  # ('clam', 'alt', 'default', 'classic')
    mystyle.configure("app.TLabel",
        foreground = "white", 
        background = "black",
        font = ('Liberation Mono', '10', 'normal')
    )  # "#4C4C4C")
    mystyle.configure("unlocked.TLabel", 
        foreground = "light green", 
        background = "black",
        font = ('Liberation Mono', '12', 'normal')
    )  # "#4C4C4C")
    mystyle.configure("smaller.TLabel", 
        foreground = "white", 
        background = "black",
        font = ('Liberation Mono', '10', 'normal')
    )  # "#4C4C4C")
    mystyle.configure("heading.TLabel",
        foreground = "white",
        background = "black",
        font = ('Liberation Mono', '36', 'normal')
    )  # "#4C4C4C")
    mystyle.configure("app.TFrame", foreground="gray55", background="black")  # "#4C4C4C",)
    mystyle.configure("app.TButton",
        foreground = "gray55", 
        background = "#D15101", 
        activeforeground = "#F2681C"
    )  # F2681C
    mystyle.configure("app.TCheckbutton", 
        foreground = "gray55",
        background = "black"
    )  # "#4C4C4C")
    mystyle.configure("app.TCombobox", 
        background = "#F2681C", 
        selectbackground = "#D15101"
    )  # postoffset = (0,0,500,0))
    mystyle.configure("app.TEntry", foreground="black", background="gray55")
    mystyle.configure("pass.TEntry",
        foreground = "gray55", 
        background = "gray55",
        insertofftime = 5000
    )
    root.option_add("*TCombobox*Listbox*selectBackground", "#D15101")

    def t(dt):
        #return matplotlib.dates.date2num(datetime.datetime.now() - datetime.timedelta(seconds=dt))
        return datetime.datetime.now() - datetime.timedelta(seconds=dt)
    def fake_start():
        ''' TODO Function Description
        '''
        return {"price_x" : [t(i) for i in range(110,0,-10)],
                "price_y" : [250, 250, 240, 240, 250, 255, 250, 240, 240, 250, 250],
                "bought_x" : [t(70), t(20) ],
                "bought_y" : [244, 244],
                "sold_x" : [t(45), t(5)],
                "sold_y" : [253, 253],
                "x_lowest_sell_order" : [t(i) for i in range(100,0,-10)],
                "y_lowest_sell_order" : [253, 253, 253, 253, 253, 253, 253, 253, 253, 253, ],
                "x_highest_buy_order" : [t(i) for i in range(100,0,-10)],
                "y_highest_buy_order" : [244, 244, 244, 244, 244, 244, 244, 244, 244, 244, ],
                }
    #test = Bot(root, root, stub = 1, title="Stub GUI (very raw)", starting_stats=fake_start())
    #test.pack()

    # ------------------------------
    # debugging:
    if False:
        import sys
        from pprint import pprint
        fake = fake_start()
        pprint(fake)

        fig, ax = plt.subplots(1, 2)
        ax[0].plot(fake["price_x"], fake["price_y"])
        ax[0].plot(fake["x_lowest_sell_order"], fake["y_lowest_sell_order"])
        ax[0].plot(fake["x_highest_buy_order"], fake["y_highest_buy_order"])
        ax[0].scatter(fake["bought_x"], fake["bought_y"])
        ax[0].scatter(fake["sold_x"], fake["sold_y"])

        hfmt = matplotlib.dates.DateFormatter('%D %H:%M:%S')
        ax[0].xaxis.set_major_formatter(hfmt)

        fig.autofmt_xdate()
        print(ax[0].get_xlim(),ax[0].get_ylim())
        #ax[0].set_xlim(ax[0].get_xlim()[0],ax[0].get_xlim()[0]+1 )
        plt.show()


        sys.exit(0)
    # ------------------------------

    app = App(root, tk.RIGHT)
    for i in range(1):
        bot = Bot(root, app(), app, stub=1, starting_stats=fake_start())
        app.add_screen(bot,
            "null", 
            textvariable=bot.title_var,
            bg="gray75",
            fg="black",
            selectcolor="lightblue"
        )
    root.after(1000, app.update_frames)
    root.mainloop()
