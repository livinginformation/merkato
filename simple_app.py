import merkato.utils.database_utils as db
from merkato.utils import generate_complete_merkato_configs
#from exchange import Exchange
from merkato.merkato import Merkato
from pprint import pprint
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.lines import Line2D

import datetime
import argparse

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
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--blockOnError', action='store_false', help="DEBUGGING ONLY: blocks all bots on error")
    args = parser.parse_args()

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

    # ------------------------------
    if db.no_merkatos_table_exists():
        db.create_merkatos_table()

    if db.no_exchanges_table_exists():
        db.create_exchanges_table()

    db.insert_exchange("test", public_api_key='abc', private_api_key='123', limit_only=True)
    merkatos = db.get_all_merkatos()
    complete_merkato_configs = generate_complete_merkato_configs(merkatos)

    # ------------------------------
    app = App(master=root, block_on_error=args["blockOnError"], side=tk.RIGHT)

    for persisted in complete_merkato_configs:
        pprint(persisted)
        bot = Bot(root, app(), app, persist=persisted)
        app.add_screen(bot,
                       "null",
                       textvariable=bot.title_var,
                       bg="gray75",
                       fg="black",
                       selectcolor="lightblue"
                       )

    for i in range(1):
        bot = Bot(root, app(), app,)
        app.add_screen(bot,
                       "null",
                       textvariable=bot.title_var,
                       bg="gray75",
                       fg="black",
                       selectcolor="lightblue"
                       )
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
    root.after(100,app.finish_new_button())

    while True:
        try:
            root.update_idletasks()
            root.update()
        except UnicodeDecodeError:
            print("Caught Scroll Error")

